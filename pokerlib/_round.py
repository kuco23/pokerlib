from operator import add
from math import inf
from random import sample
from collections import namedtuple, deque
from abc import ABC

from .enums import *
from ._handparser import HandParser, HandParserGroup


"""
╔════════════════════════════════════════════════╗
║                                                ║
║   Round philosophy:                            ║
║   The information about the state of game      ║
║   should be kept within one object.            ║
║   That object has a generator-like property,   ║
║   so that, when sent valid input,              ║
║   it updates properties which make it          ║
║   ready for the next valid input.              ║
║                                                ║
╚════════════════════════════════════════════════╝ 
"""

# Round's user input interface includes:
# - validate checks (can't check when call is needed)
# - validating raises (can't raise if funds are too low to call)

# Round's implementation includes
# - recognizing implicit all ins (player call exceeds his funds)

# kwargs arguments for publicOut and privateOut are
# basic immutable round objects.
# additional Round attributes can be cached by overriding 
# publicOut and privateOut methods, when needed for io purposes

class AbstractRound(ABC):
    __deck = [[rank, suit] for suit in Suit for rank in Rank]

    def __init__(self, _id, players, button, small_blind, big_blind):
        self.id = _id
        self.finished = False

        self.small_blind = small_blind
        self.big_blind = big_blind

        self.players = players
        self.button = button
        self.current_index = button

        self.board = list()
        self.turn = None
        
        self._deck = self._deckIterator()
        self._turn_generator = self._turnGenerator()

        self.publicOut(RoundPublicOutId.NEWROUND)

        for player in self.players:
            player.resetState()
            player.cards = (next(self._deck), next(self._deck))
            player.hand = HandParser(list(player.cards))

            self.privateOut(
                player.id,
                RoundPrivateOutId.DEALTCARDS
            )

        next(self._turn_generator)
        self._dealBlinds()
        self._processState()
    
    def __repr__(self):
        return f'Round({self.players}, {self.board})'

    def __bool__(self):
        return not self.finished

    def __contains__(self, player):
        return player in self.players

    def __getitem__(self, _id):
        return self.players.getPlayerById(_id)

    @property
    def current_player(self):
        return self.players[self.current_index]

    @property
    def turn_stake(self):
        return max(map(
            lambda player: player.turn_stake[self.turn],
            self.players
        ))

    @property
    def pot_size(self):
        return list(map(lambda i: sum(map(
            lambda player: player.turn_stake[i],
            self.players
        )), range(4)))

    @property
    def to_call(self):
        called = self.current_player.turn_stake[self.turn]
        return self.turn_stake - called

    def _deckIterator(self):
        ncards = len(self.players) * 2 + 5
        return iter(sample(self.__deck, ncards))

    def _turnGenerator(self):
        for i, turn in zip((0,3,1,1), Turn):
            self.turn = turn
            new_cards = [next(self._deck) for _ in range(i)]

            for player in self.players:
                player.played_turn = False
                player.hand += new_cards
                player.hand.parse()

            self.board.extend(new_cards)

            self.publicOut(
                RoundPublicOutId.NEWTURN,
                turn = turn
            )

            yield

    def _shiftCurrentPlayer(self):
        i = self.current_index
        self.current_index = self.players.nextActiveIndex(i)
    
    def _pots_balanced(self):
        active_pots = [
            player.turn_stake[self.turn]
            for player in self.players
            if player.is_active
        ] or [inf]

        all_in_max_pot = max([
            player.turn_stake[self.turn]
            for player in self.players
            if player.is_all_in
        ] or [0])

        return (
            len(set(active_pots)) == 1 and
            active_pots[0] >= all_in_max_pot
        )

    def _addToPot(self, player, money):
        if 0 <= money < player.money:
            player.money -= money
            player.turn_stake[self.turn] += money
            player.stake += money
        else:
            all_in_stake = player.money
            player.turn_stake[self.turn] += all_in_stake
            player.stake += all_in_stake
            player.money = 0
            player.is_all_in = True

            self.publicOut(
                RoundPublicOutId.PLAYERALLIN,
                player_id = player.id,
                all_in_stake = all_in_stake
            )

    def _dealBlinds(self):
        i = self.current_index

        previous_player = self.players.previousActivePlayer(i)
        self._addToPot(previous_player, self.small_blind)

        self.publicOut(
            RoundPublicOutId.SMALLBLIND,
            player_id = previous_player.id,
            turn_stake = previous_player.turn_stake[0]
        )

        self._addToPot(self.current_player, self.big_blind)

        self.publicOut(
            RoundPublicOutId.BIGBLIND,
            player_id = self.current_player.id,
            turn_stake = self.current_player.turn_stake[0]
        )

    def _dealPrematureWinnings(self):
        winner = self.players.getNotFoldedPlayers()[0]
        won = sum(self.pot_size)
        winner.money += won

        self.publicOut(
            RoundPublicOutId.DECLAREPREMATUREWINNER,
            player_id = winner.id,
            money_won = won,
        )

    def _dealWinnings(self):
        stake_sorted = type(self.players)(add(
            sorted(
                [player for player in self.players if player.is_all_in],
                key = lambda player: player.stake
            ),
            sorted(
                [player for player in self.players if player.is_active],
                key = lambda player: player.stake
            )
        ))

        for competitor in stake_sorted:
            self.publicOut(
                RoundPublicOutId.PUBLICCARDSHOW,
                player_id = competitor.id
            )

        grouped_indexes = [0]
        for i in range(1, len(stake_sorted)):
            if stake_sorted[i - 1].stake < stake_sorted[i].stake:
                grouped_indexes.append(i)

        for i in grouped_indexes:
            subgame_competitors = stake_sorted[i:]
            subgame_stake = subgame_competitors[0].stake

            hands = [p.hand for p in subgame_competitors]
            hands = HandParserGroup(hands)
            kickers = hands.getGroupKicker()

            winning_players = subgame_competitors.winners()
            nsplit = len(winning_players)

            take_from = []
            for player in self.players:
                if 0 < player.stake <= subgame_stake:
                    take_from.append(player.stake / nsplit)
                elif 0 < subgame_stake <= player.stake:
                    take_from.append(subgame_stake / nsplit)
                else: take_from.append(0)

            for win_split in winning_players:
                win_took = 0

                for player, take in zip(self.players, take_from):
                    win_took += take
                    player.stake -= take

                if round(win_took):
                    win_split.money += round(win_took)

                    self.publicOut(
                        RoundPublicOutId.DECLAREFINISHEDWINNER,
                        player_id = win_split.id,
                        money_won = round(win_took),
                        kickers = kickers
                    )

    def _processState(self):
        active = len(self.players.getActivePlayers())
        not_folded = len(self.players.getNotFoldedPlayers())
        pots_balanced = self._pots_balanced()

        if not_folded == 0:
            return self._close()

        elif not_folded == 1:
            self._dealPrematureWinnings()
            return self._close()

        elif active <= 1 and pots_balanced:
            for _ in self._turn_generator: pass
            self._dealWinnings()
            return self._close()

        elif self.players.allPlayedTurn() and pots_balanced:
            if self.turn == Turn.RIVER:
                self._dealWinnings()
                return self._close()
            else:
                self.current_index = self.button
                next(self._turn_generator)

        self._shiftCurrentPlayer()
        called = self.current_player.turn_stake[self.turn]

        self.publicOut(
            RoundPublicOutId.PLAYERACTIONREQUIRED,
            player_id = self.current_player.id,
            to_call = self.turn_stake - called
        )

    def _fold(self):
        self.current_player.is_folded = True
        self.publicOut(
            RoundPublicOutId.PLAYERFOLD,
            player_id = self.current_player.id
        )

    def _check(self):
        self.publicOut(
            RoundPublicOutId.PLAYERCHECK,
            player_id = self.current_player.id
        )

    def _call(self):
        to_call = self.to_call
        self._addToPot(self.current_player, to_call)
        self.publicOut(
            RoundPublicOutId.PLAYERCALL,
            player_id = self.current_player.id,
            called = to_call
        )

    def _raise(self, raise_by):
        to_call= self.to_call
        self._addToPot(self.current_player, to_call + raise_by)
        self.publicOut(
            RoundPublicOutId.PLAYERRAISE,
            player_id = self.current_player.id,
            raised_by = raise_by
        )

    def _allin(self):
        cp = self.current_player
        self._addToPot(cp, cp.money)

    def _executeAction(self, action, raise_by):
        if action is RoundPublicInId.FOLD:
            self._fold()
        elif action is RoundPublicInId.CHECK:
            self._check()
        elif action is RoundPublicInId.CALL:
            self._call()
        elif action is RoundPublicInId.RAISE:
            self._raise(raise_by)
        elif action is RoundPublicInId.ALLIN:
            self._allin()

    def _processAction(self, action, raise_by=0):
        self._executeAction(action, raise_by)
        self.current_player.played_turn = True
        self._processState() 

    def _close(self):
        self.finished = True
        self.publicOut(RoundPublicOutId.ROUNDFINISHED)
    
    def publicIn(self, player_id, action, **kwargs):
        """Processes invalidated user input"""
        ...
        
    def privateOut(self, player_id, out_id, **kwargs):
        """Override player out implementation"""
        ...

    def publicOut(self, out_id, **kwargs):
        """Override game out implementation"""
        ...


class Round(AbstractRound):
    PublicOut = namedtuple('PublicOut', ['id', 'data'])
    PrivateOut = namedtuple('PrivateOut', ['player_id', 'id', 'data'])

    def __init__(self, *args):
        self.public_out_queue = deque([])
        self.private_out_queue = deque([])
        super().__init__(*args)

    def publicIn(self, player_id, action, raise_by=0):
        # public in must come from current player
        player = self.current_player
        if player_id != player.id: return

        to_call = self.turn_stake - player.turn_stake[self.turn]
        if action is RoundPublicInId.CHECK and to_call == 0:
            self._processAction(RoundPublicInId.CHECK)
        elif action is RoundPublicInId.RAISE:
           if to_call < player.money:
                self._processAction(RoundPublicInId.RAISE, raise_by)
        elif (
            action is RoundPublicInId.CALL or 
            action is RoundPublicInId.ALLIN or 
            action is RoundPublicInId.FOLD 
        ): self._processAction(action, raise_by)

    def privateOut(self, player_id, out_id, **kwargs):
        """Player out implementation"""
        # A solution for interacting with an outside io
        kwargs.update(self.extendedPrivateOut(player_id, out_id, kwargs))
        out = self.PrivateOut(player_id, out_id, kwargs)
        self.private_out_queue.append(out)

    def publicOut(self, out_id, **kwargs):
        """Game out implementation"""
        # A solution for interacting with an outside io
        kwargs.update(self.extendedPublicOut(out_id, kwargs))
        out = self.PublicOut(out_id, kwargs)
        self.public_out_queue.append(out)
    
    def extendedPrivateOut(self, player_id, out_id, kwargs):
        """Relevant private-out arguments from round instance state"""
        player = self.players.getPlayerById(player_id)
        if out_id is RoundPrivateOutId.DEALTCARDS:
            return {'cards': player.cards}
        else: return dict()
        
    def extendedPublicOut(self, out_id, kwargs):
        """Relevant public-out arguments from round instance state"""
        if out_id is RoundPublicOutId.NEWTURN:
            return {'board': self.board}
        elif out_id is RoundPublicOutId.SMALLBLIND: 
            return {'small_blind': self.small_blind} 
        elif out_id is RoundPublicOutId.BIGBLIND:
            return {'big_blind': self.big_blind}
        elif out_id is RoundPublicOutId.PUBLICCARDSHOW:
            player = self.players.getPlayerById(kwargs['player_id'])
            return {'cards': player.cards}
        elif out_id is RoundPublicOutId.DECLAREFINISHEDWINNER:
            player = self.players.getPlayerById(kwargs['player_id'])
            return {
                'cards': player.cards, 
                'handname': player.hand.handenum,
                'hand': player.hand.handbasecards
            }
        else: return dict()
    
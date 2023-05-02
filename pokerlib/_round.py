from math import inf
from random import sample
from collections import namedtuple, deque
from abc import ABC

from .enums import Rank, Suit, Turn, RoundPublicInId, RoundPrivateOutId, RoundPublicOutId
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
    PublicInId = RoundPublicInId
    PublicOutId = RoundPublicOutId
    PrivateOutId = RoundPrivateOutId
    __deck = [[rank, suit] for suit in Suit for rank in Rank]

    def __init__(self, _id, players, button, small_blind, big_blind):
        self.id = _id
        self.finished = False
        self.closed = False

        self.small_blind = small_blind
        self.big_blind = big_blind

        self.players = players
        self.button = button
        self.current_index = button # it will move

        self.board = list()
        self.turn = None

        self._deck = self._deckIterator()
        self._turn_generator = self._turnGenerator()
        self._muck_optioned_player_ids = []

        self._startRound()

    def __repr__(self):
        return f'Round({self.players}, {self.board})'

    def __bool__(self):
        return not self.closed

    def __contains__(self, player):
        return player in self.players

    def __getitem__(self, _id):
        return self.players.getPlayerById(_id)

    @property
    def starting_player_index(self):
        return self.players.nextUnfoldedIndex(self.button)
    @property
    def last_aggressor_index(self):
        return self.players.previousUnfoldedIndex(
            self.current_index)
    @property
    def small_blind_player_index(self):
        return self.button - 2 if len(self.players) > 2 else self.button - 1
    @property
    def big_blind_player_index(self):
        return self.button - 1 if len(self.players) > 2 else self.button

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
                self.PublicOutId.NEWTURN,
                turn = turn
            )

            yield

    def _potsBalanced(self):
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
            return money
        else:
            all_in_stake = player.money
            player.turn_stake[self.turn] += all_in_stake
            player.stake += all_in_stake
            player.money = 0
            player.is_all_in = True

            self.publicOut(
                self.PublicOutId.PLAYERISALLIN,
                player_id = player.id,
                all_in_stake = all_in_stake
            )
            return all_in_stake

    def _startRound(self):
        self.publicOut(self.PublicOutId.NEWROUND)

        for player in self.players:
            player.resetState()
            player.cards = (next(self._deck), next(self._deck))
            player.hand = HandParser(list(player.cards))

            self.privateOut(
                player.id,
                self.PrivateOutId.DEALTCARDS
            )

        next(self._turn_generator)
        self._dealSmallBlind()
        self._dealBigBlind()
        self._postActionStateUpdate()

    def _dealSmallBlind(self):
        small_blind_player = self.players[self.small_blind_player_index]
        paid_amount = self._addToPot(small_blind_player, self.small_blind)
        self.publicOut(
            self.PublicOutId.SMALLBLIND,
            player_id = small_blind_player.id,
            paid_amount = paid_amount
        )

    def _dealBigBlind(self):
        big_blind_player = self.players[self.big_blind_player_index]
        paid_amount = self._addToPot(big_blind_player, self.big_blind)
        self.publicOut(
            self.PublicOutId.BIGBLIND,
            player_id = big_blind_player.id,
            paid_amount = paid_amount
        )

    def _dealPrematureWinnings(self):
        winner, = self.players.getNotFoldedPlayers()
        won = sum(self.pot_size)
        winner.money += won

        self.publicOut(
            self.PublicOutId.DECLAREPREMATUREWINNER,
            player_id = winner.id,
            money_won = won,
        )

        self._muck_optioned_player_ids.append(winner.id)

        self.publicOut(
            self.PublicOutId.PLAYERCHOICEREQUIRED,
            player_id = winner.id
        )

    def _dealWinnings(self):
        stake_sorted = self.players.sortedByWinningAmountProspect()

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
                    win_split.group_kickers = kickers

                    self.publicOut(
                        self.PublicOutId.DECLAREFINISHEDWINNER,
                        player_id = win_split.id,
                        money_won = round(win_took)
                    )

        self._showdown()

    def _showdown(self):
        showdown_initiator_index = self.last_aggressor_index \
            if self.turn_stake > 0 else self.starting_player_index
        current_best_hand = self.players[showdown_initiator_index].hand
        for i in range(len(self.players)):
            player = self.players[showdown_initiator_index + i]
            if player.is_folded: continue
            if i == 0 or player.hand >= current_best_hand:
                current_best_hand = player.hand
                self.publicOut(
                    self.PublicOutId.PUBLICCARDSHOW,
                    player_id = player.id,
                    cards = player.cards,
                    kickers = player.group_kickers
                )
            else:
                self._muck_optioned_player_ids.append(player.id)
                self.publicOut(
                    self.PublicOutId.PLAYERCHOICEREQUIRED,
                    player_id = player.id,
                )

    def _shiftCurrentPlayer(self):
        self.current_index = self.players.nextActiveIndex(
            self.current_index)

    def _moveToNextPlayer(self):
        self._shiftCurrentPlayer()
        called = self.current_player.turn_stake[self.turn]
        self.publicOut(
            self.PublicOutId.PLAYERACTIONREQUIRED,
            player_id = self.current_player.id,
            to_call = self.turn_stake - called
        )

    def _postActionStateUpdate(self, is_update_after_forcefold=False):
        active = self.players.countActivePlayers()
        not_folded = self.players.countUnfoldedPlayers()
        pots_balanced = self._potsBalanced()

        if not_folded == 0:
            return self._close()

        elif not_folded == 1:
            self._dealPrematureWinnings()
            return self._finish()

        elif active <= 1 and pots_balanced:
            for _ in self._turn_generator: pass
            self._dealWinnings()
            return self._finish()

        elif self.players.allPlayedTurn() and pots_balanced:
            if self.turn == Turn.RIVER:
                self._dealWinnings()
                return self._finish()
            else:
                next(self._turn_generator)
                self.current_index = self.button
                return self._moveToNextPlayer()

        # this function can be called after a non-current-player's
        # hand is force-folded, in which case we don't want to move
        # onto the next player
        elif not is_update_after_forcefold:
            self._moveToNextPlayer()

    def _fold(self):
        self.current_player.is_folded = True
        self.publicOut(
            self.PublicOutId.PLAYERFOLD,
            player_id = self.current_player.id
        )

    def _check(self):
        self.publicOut(
            self.PublicOutId.PLAYERCHECK,
            player_id = self.current_player.id
        )

    def _call(self):
        to_call = self.to_call
        paid_amount = self._addToPot(self.current_player, to_call)
        self.publicOut(
            self.PublicOutId.PLAYERCALL,
            player_id = self.current_player.id,
            paid_amount = paid_amount
        )

    def _raise(self, raise_by):
        to_call = self.to_call
        paid_amount = self._addToPot(self.current_player, to_call + raise_by)
        self.publicOut(
            self.PublicOutId.PLAYERRAISE,
            player_id = self.current_player.id,
            raised_by = raise_by,
            paid_amount = paid_amount
        )

    def _allin(self):
        cp = self.current_player
        paid_amount = self._addToPot(cp, cp.money)
        self.publicOut(
            self.PublicOutId.PLAYERWENTALLIN,
            player_id = self.current_player.id,
            paid_amount = paid_amount
        )

    def _show(self, player_id):
        self._muck_optioned_player_ids.remove(player_id)
        player = self.players.getPlayerById(player_id)
        self.publicOut(
            self.PublicOutId.PLAYERREVEALCARDS,
            player_id = player_id,
            cards = player.cards
        )

    def _muck(self, player_id):
        self._muck_optioned_player_ids.remove(player_id)
        self.publicOut(
            self.PublicOutId.PLAYERMUCKCARDS,
            player_id = player_id
        )

    def _executeAction(self, action, raise_by):
        if action is self.PublicInId.FOLD:
            self._fold()
        elif action is self.PublicInId.CHECK:
            self._check()
        elif action is self.PublicInId.CALL:
            self._call()
        elif action is self.PublicInId.RAISE:
            self._raise(raise_by)
        elif action is self.PublicInId.ALLIN:
            self._allin()

    def _executeChoice(self, choice, player_id):
        if choice is self.PublicInId.SHOW:
            self._show(player_id)
        elif choice is self.PublicInId.MUCK:
            self._muck(player_id)
        if self._muck_optioned_player_ids == []:
            self._close()

    def _processAction(self, action, raise_by=0):
        self._executeAction(action, raise_by)
        self.current_player.played_turn = True
        self._postActionStateUpdate()

    def _finish(self):
        self.finished = True
        self.publicOut(self.PublicOutId.ROUNDFINISHED)

    def _close(self):
        self.closed = True
        self.publicOut(self.PublicOutId.ROUNDCLOSED)

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
        if self.closed: return # can't do anything if round is closed
        if self.finished: # if round is finished, only show/muck is allowed
            if action is self.PublicInId.SHOW or action is self.PublicInId.MUCK:
                if player_id in self._muck_optioned_player_ids:
                    self._executeChoice(action, player_id)
        elif ( # if round is not finished, only valid actions are allowed
            action is self.PublicInId.CHECK or
            action is self.PublicInId.CALL or
            action is self.PublicInId.FOLD or
            action is self.PublicInId.ALLIN or
            action is self.PublicInId.RAISE
        ):
            player = self.current_player
            if player_id != player.id: return
            to_call = self.turn_stake - player.turn_stake[self.turn]
            if action is self.PublicInId.CHECK and to_call == 0:
                self._processAction(self.PublicInId.CHECK)
            elif action is self.PublicInId.RAISE:
                if to_call < player.money:
                    self._processAction(self.PublicInId.RAISE, raise_by)
            else: self._processAction(action, raise_by)

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
        if out_id is self.PrivateOutId.DEALTCARDS:
            return {'cards': player.cards}
        else: return dict()

    def extendedPublicOut(self, out_id, kwargs):
        """Relevant public-out arguments from round instance state"""
        if out_id is self.PublicOutId.NEWTURN:
            return {'board': self.board}
        elif out_id is self.PublicOutId.SMALLBLIND:
            return {'small_blind': self.small_blind}
        elif out_id is self.PublicOutId.BIGBLIND:
            return {'big_blind': self.big_blind}
        elif out_id is self.PublicOutId.PUBLICCARDSHOW:
            player = self.players.getPlayerById(kwargs['player_id'])
            return {'cards': player.cards}
        elif out_id is self.PublicOutId.DECLAREFINISHEDWINNER:
            player = self.players.getPlayerById(kwargs['player_id'])
            return {
                'cards': player.cards,
                'handname': player.hand.handenum,
                'hand': list(player.hand.handbasecards)
            }
        else: return dict()

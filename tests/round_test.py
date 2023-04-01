import sys
sys.path.append('../pokerlib')
from copy import deepcopy
from pokerlib.enums import Turn
from pokerlib import Table, Player, PlayerGroup

class OutReturnTable(Table):
    cachedOutput = []
    def publicIn(self, player_id, action, **kwargs):
        super().publicIn(player_id, action, **kwargs)
        outputs = deepcopy(self.cachedOutput)
        self.cachedOutput.clear()
        return outputs
    def publicOut(self, _id, **kwargs):
        self.cachedOutput.append((_id, kwargs))
    def privateOut(self, _id, player_id, **kwargs):
        self.cachedOutput.append((_id, player_id, kwargs))

player1 = Player(0, 1, "player1", 1000)
player2 = Player(0, 2, "player2", 1000)
players = PlayerGroup([player1, player2])
table = OutReturnTable(0, 6, players, 1000, 5, 10)

# initial table outputs (in constructor)
player1joined, player2joined = table.cachedOutput
_id, kwargs = player1joined
assert _id is table.PublicOutId.PLAYERJOINED
assert kwargs['player_id'] == 1
_id, kwargs = player2joined
assert _id is table.PublicOutId.PLAYERJOINED
assert kwargs['player_id'] == 2
table.cachedOutput.clear()

# starting round - deal cards, blinds, require call big blind action
response = table.publicIn(player1.id, table.PublicInId.STARTROUND)
new_round_started, dealt_cards1, dealt_cards2, new_round, turn_preflop, small_blind, big_blind, required_call = response
_id, kwargs = new_round_started
assert _id is table.PublicOutId.NEWROUNDSTARTED
player_id, _id, kwargs = dealt_cards1
assert _id is table.round.PrivateOutId.DEALTCARDS
assert len(kwargs['cards']) == 2
player_id, _id, kwargs = dealt_cards2
assert _id is table.round.PrivateOutId.DEALTCARDS
assert len(kwargs['cards']) == 2
_id, kwargs = new_round
assert _id is table.round.PublicOutId.NEWROUND
_id, kwargs = turn_preflop
assert _id is table.round.PublicOutId.NEWTURN
assert kwargs['turn'] is Turn.PREFLOP
assert kwargs['board'] == []
_id, kwargs = small_blind
assert _id is table.round.PublicOutId.SMALLBLIND
assert kwargs['small_blind'] == 5
assert kwargs['turn_stake'] == 5
_id, kwargs = big_blind
assert _id is table.round.PublicOutId.BIGBLIND
assert kwargs['big_blind'] == 10
assert kwargs['turn_stake'] == 10
_id, kwargs = required_call
assert _id is table.round.PublicOutId.PLAYERACTIONREQUIRED
assert kwargs['to_call'] == 5

# call big blind, action required is check/raise from big-blind player
called, required_check = table.publicIn(player1.id, table.round.PublicInId.CALL)
_id, kwargs = called
assert _id is table.round.PublicOutId.PLAYERCALL
assert kwargs['called'] == 5
_id, kwargs = required_check
assert _id is table.round.PublicOutId.PLAYERACTIONREQUIRED
assert kwargs['to_call'] == 0

# check from the big-blind player, expect new turn
checked, turn_flop, required_check = table.publicIn(player2.id, table.round.PublicInId.CHECK)
_id, kwargs = checked
assert _id is table.round.PublicOutId.PLAYERCHECK
_id, kwargs = turn_flop
assert _id is table.round.PublicOutId.NEWTURN
assert kwargs['turn'] is Turn.FLOP
assert len(kwargs['board']) == 3
_id, kwargs = required_check
assert _id is table.round.PublicOutId.PLAYERACTIONREQUIRED
assert kwargs['to_call'] == 0

# check from the small-blind player
checked, required_check = table.publicIn(player1.id, table.round.PublicInId.CHECK)
_id, kwargs = checked
assert _id is table.round.PublicOutId.PLAYERCHECK
_id, kwargs = turn_flop
_id, kwargs = required_check
assert _id is table.round.PublicOutId.PLAYERACTIONREQUIRED
assert kwargs['to_call'] == 0

# player raises
raised, required_call = table.publicIn(player2.id, table.round.PublicInId.RAISE, raise_by=50)
_id, kwargs = raised
assert _id is table.round.PublicOutId.PLAYERRAISE
assert kwargs['raised_by'] == 50
_id, kwargs = required_call
assert _id is table.round.PublicOutId.PLAYERACTIONREQUIRED
assert kwargs['to_call'] == 50

# player calls, expect new turn
called, turn_turn, required_check = table.publicIn(player1.id, table.round.PublicInId.CALL)
_id, kwargs = called
assert _id is table.round.PublicOutId.PLAYERCALL
assert kwargs['called'] == 50
_id, kwargs = turn_turn
assert _id is table.round.PublicOutId.NEWTURN
assert kwargs['turn'] == Turn.TURN
assert len(kwargs['board']) == 4
_id, kwargs = required_check
assert _id is table.round.PublicOutId.PLAYERACTIONREQUIRED
assert kwargs['to_call'] == 0

# player checks
check, required_check = table.publicIn(player1.id, table.round.PublicInId.CHECK)
_id, kwargs = check
assert _id is table.round.PublicOutId.PLAYERCHECK
_id, kwargs = required_check
assert _id is table.round.PublicOutId.PLAYERACTIONREQUIRED
assert kwargs['to_call'] == 0

# player checks
check, turn_river, required_check = table.publicIn(player2.id, table.round.PublicInId.CHECK)
_id, kwargs = check
assert _id is table.round.PublicOutId.PLAYERCHECK
_id, kwargs = turn_river
assert _id is table.round.PublicOutId.NEWTURN
assert kwargs['turn'] == Turn.RIVER
assert len(kwargs['board']) == 5
_id, kwargs = required_check
assert _id is table.round.PublicOutId.PLAYERACTIONREQUIRED
assert kwargs['to_call'] == 0

# player moves all in
allin, required_call = table.publicIn(player1.id, table.round.PublicInId.ALLIN)
_id, kwargs = allin
assert _id is table.round.PublicOutId.PLAYERALLIN
assert kwargs['all_in_stake'] == 940
_id, kwargs = required_call
assert _id is table.round.PublicOutId.PLAYERACTIONREQUIRED
assert kwargs['to_call'] == 940

# player calls, expect game resolution
response = table.publicIn(player2.id, table.round.PublicInId.CALL)
allin, called, show_cards1, show_cards2, declare_winner, *_non_determinstic = response
_id, kwargs = allin
assert _id is table.round.PublicOutId.PLAYERALLIN
assert kwargs['all_in_stake'] == 940
_id, kwargs = called
assert _id is table.round.PublicOutId.PLAYERCALL
assert kwargs['called'] == 940
_id, kwargs = show_cards1
assert _id is table.round.PublicOutId.PUBLICCARDSHOW
assert len(kwargs['cards']) == 2
_id, kwargs = show_cards2
assert _id is table.round.PublicOutId.PUBLICCARDSHOW
assert len(kwargs['cards']) == 2
_id, kwargs = declare_winner
assert _id is table.round.PublicOutId.DECLAREFINISHEDWINNER
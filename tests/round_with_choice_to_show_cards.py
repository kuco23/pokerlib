import sys
sys.path.append('../pokerlib')
from copy import deepcopy
from pokerlib import Player, PlayerSeats
from pokerlib.implementations import TableWithChoiceToShowCards

class OutReturnTable(TableWithChoiceToShowCards):
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
seats = PlayerSeats([player1, player2])
table = OutReturnTable(0, seats, 1000, 5, 10)

table.publicIn(player1.id, table.PublicInId.STARTROUND)
table.publicIn(player1.id, table.round.PublicInId.CALL)
table.publicIn(player2.id, table.round.PublicInId.CALL)
table.publicIn(player1.id, table.round.PublicInId.ALLIN)
table.publicIn(player2.id, table.round.PublicInId.FOLD)
table.publicIn(player1.id, table.round.PublicInId.SHOWCARDS, show_cards=True)
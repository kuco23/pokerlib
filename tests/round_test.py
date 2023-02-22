import sys
sys.path.append('../pokerlib')

from pokerlib.enums import RoundPublicInId, TablePublicInId
from pokerlib import Table, Player, PlayerGroup

player1 = Player(0, 1, "player1", 1000)
player2 = Player(0, 2, "player2", 1000)
players = PlayerGroup([player1, player2])
table = Table(0, 6, players, 1000, 10, 5)

table.publicIn(player1.id, TablePublicInId.STARTROUND)
table.publicIn(player1.id, RoundPublicInId.CALL)
table.publicIn(player2.id, RoundPublicInId.CHECK)
table.publicIn(player1.id, RoundPublicInId.CHECK)
table.publicIn(player2.id, RoundPublicInId.RAISE, raise_by=50)
table.publicIn(player1.id, RoundPublicInId.CALL)
table.publicIn(player1.id, RoundPublicInId.CHECK)
table.publicIn(player2.id, RoundPublicInId.CHECK)
table.publicIn(player1.id, RoundPublicInId.ALLIN)
table.publicIn(player2.id, RoundPublicInId.CALL)
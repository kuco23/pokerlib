import sys
sys.path.append('../pokerlib')
from pokerlib import Table, Player, PlayerSeats

seats = PlayerSeats([None] * 9)
table = Table(0, seats, 1000, 5, 10)

player1 = Player(0, 1, "player1", 1000)
player2 = Player(0, 2, "player2", 1000)
player3 = Player(0, 3, "player3", 1000)
player4 = Player(0, 4, "player4", 1000)
player5 = Player(0, 5, "player5", 1000)
player6 = Player(0, 6, "player6", 1000)
player7 = Player(0, 7, "player7", 1000)
player8 = Player(0, 8, "player8", 1000)
player9 = Player(0, 9, "player9", 1000)

table += player1, 0
table += player2, 2

assert len(table) == 9
assert table[0].id == player1.id
assert table[2].id == player2.id
for i in range(9):
    if i == 0 or i == 2:
        continue
    assert table[i] is None

table += player3
table += player4
assert table[1].id == player3.id
assert table[3].id == player4.id

table.publicIn(player5.id, table.PublicInId.BUYIN, player=player5, buyin=1000, index=8)
assert table[8].id == player5.id

table.publicIn(player6.id, table.PublicInId.BUYIN, player=player6, buyin=1000)
assert table[4].id == player6.id

table += player7
table += player8, 6
table += player9

assert table[5].id == player7.id
assert table[6].id == player8.id
assert table[7].id == player9.id
import sys
sys.path.append('../pokerlib')

import pokerlib
from pokerlib import enums
from pokerlib.implementations import NoMuckShowdownTable

class MyTable(NoMuckShowdownTable):
    def publicOut(self, out_id, **kwargs):
        if 'hand' in kwargs:
            kwargs['hand'] = list(kwargs['hand'])
        if out_id.name == enums.RoundPublicOutId.SMALLBLIND.name:
            group = self.round.players
            print(
                f'DEALER index {self.round.button}, player {group[self.round.button].id} - {group[self.round.button]}')
            kwargs['dealer_id'] = group[self.round.button].id
        print("pub", out_id.name, kwargs)

    def privateOut(self, player_id, out_id, **kwargs):
        if 'hand' in kwargs:
            kwargs['hand'] = list(kwargs['hand'])
        print("private", out_id, kwargs)


table = MyTable(
    _id=10,
    seats=pokerlib.PlayerSeats([None] * 5),
    buyin=150,
    small_blind=5,
    big_blind=10,
)
player1 = pokerlib.Player(
    table_id=table.id,
    _id=11,
    name='alice',
    money=table.buyin
)
player2 = pokerlib.Player(
    table_id=table.id,
    _id=12,
    name='bob',
    money=table.buyin
)
player3 = pokerlib.Player(
    table_id=table.id,
    _id=13,
    name='uncle joe',
    money=table.buyin

)
player4 = pokerlib.Player(
    table_id=table.id,
    _id=14,
    name='bro kat',
    money=table.buyin

)
table += (player1, 0)
table += (player2, 1)
table += (player3, 2)
table += (player4, 3)
table.publicIn(player1.id, enums.TablePublicInId.STARTROUND)

table.publicIn(player3.id, table.round.PublicInId.CALL)
table.publicIn(player4.id, table.round.PublicInId.CALL)
table.publicIn(player1.id, table.round.PublicInId.CALL)
table.publicIn(player2.id, table.round.PublicInId.CALL)
table.publicIn(player3.id, table.round.PublicInId.CALL)
table.publicIn(player4.id, table.round.PublicInId.CALL)
table.publicIn(player1.id, table.round.PublicInId.CALL)
table.publicIn(player2.id, table.round.PublicInId.CALL)
table.publicIn(player3.id, table.round.PublicInId.CALL)
table.publicIn(player4.id, table.round.PublicInId.CALL)
table.publicIn(player1.id, table.round.PublicInId.CALL)
table.publicIn(player2.id, table.round.PublicInId.CALL)
table.publicIn(player3.id, table.round.PublicInId.CALL)
table.publicIn(player4.id, table.round.PublicInId.CALL)
table.publicIn(player1.id, table.round.PublicInId.CALL)
table.publicIn(player2.id, table.round.PublicInId.CALL)
table.publicIn(player3.id, table.round.PublicInId.CALL)
table.publicIn(player4.id, table.round.PublicInId.CALL)

# try to remove block
table.publicIn(player1.id, table.round.PublicInId.MUCK)
table.publicIn(player2.id, table.round.PublicInId.MUCK)
table.publicIn(player3.id, table.round.PublicInId.MUCK)
table.publicIn(player4.id, table.round.PublicInId.MUCK)
table.publicIn(player1.id, table.round.PublicInId.SHOW)
table.publicIn(player2.id, table.round.PublicInId.SHOW)
table.publicIn(player3.id, table.round.PublicInId.SHOW)
table.publicIn(player4.id, table.round.PublicInId.SHOW)

table.publicIn(player1.id, enums.TablePublicInId.STARTROUND)
table.publicIn(player2.id, enums.TablePublicInId.STARTROUND)
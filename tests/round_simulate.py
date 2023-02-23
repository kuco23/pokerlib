import sys
sys.path.append('../pokerlib')

from argparse import ArgumentParser
from pokerlib.enums import *
from pokerlib import HandParser
from pokerlib import Player, PlayerGroup
from pokerlib import Table, Round

class MyTable(Table):

    def publicOut(self, _id, **kwargs):
        super().publicOut(_id, **kwargs)
        print(_id, kwargs)
    def privateOut(self, _id, player, **kwargs):
        super().privateOut(_id, player, **kwargs)
        print(_id, player, kwargs)

def roundSimulation(nplayers, buyin, sb, bb):
    players = PlayerGroup(map(
        lambda i: Player(None, i, f"player{i}", buyin),
        range(nplayers)
    ))

    table = MyTable(None, nplayers, players, buyin, sb, bb)

    while table:
        while table and not table.round:
            table.publicIn(
                table.players[0].id,
                TablePublicInId.STARTROUND
            )

        player = table.round.current_player
        inp = input(f"require input from {player.id}: ")

        if inp in RoundPublicInId.__members__:
            action, raise_by = RoundPublicInId.__members__[inp], 0
        elif inp.startswith(RoundPublicInId.RAISE.name):
            raise_by = int(inp.split()[1])
            action, raise_by = RoundPublicInId.RAISE, raise_by
        else:
            continue

        table.publicIn(player.id, action, raise_by=raise_by)


args = ArgumentParser(
    description = 'Test for the poker round continuation'
)
args.add_argument(
    'npl', metavar = 'number of players',
    type = int
)
args.add_argument(
    '-bi', metavar = 'default player buyin',
    type = int, default = 1000
)
args.add_argument(
    '-sb', metavar = 'default round small blind',
    type = int, default = 10
)
args.add_argument(
    '-bb', metavar = 'default round big blind',
    type = int, default = 20
)
vals = args.parse_args()

roundSimulation(vals.npl, vals.bi, vals.sb, vals.bb)

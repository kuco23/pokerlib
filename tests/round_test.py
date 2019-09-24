from sys import path
from pathlib import Path
from argparse import ArgumentParser

path.append(str(Path().cwd().parent))

from pokerlib.enums import *
from pokerlib import HandParser
from pokerlib import Player, PlayerGroup
from pokerlib import Table, Round

actiondict = {
    'call': PlayerAction.CALL,
    'fold': PlayerAction.FOLD,
    'check': PlayerAction.CHECK,
    'all in': PlayerAction.ALLIN
}

class Round(Round):

    def publicOut(self, _id, **kwargs):
        print(_id, kwargs)
    def privateOut(self, _id, player, **kwargs):
        print(_id, player, kwargs)
    def privateIn(self, player_id, action, raise_by=0):
        self.processAction(action, raise_by)

Table.Round = Round

def roundSimulation(nplayers, money, sb, bb):
    players = PlayerGroup(map(
        lambda i: Player(None, i, f"user{i}", money),
        range(nplayers)
    ))
    
    table = Table(None, players, sb, bb)

    while table:
        while table and not table.round:
            table.newRound(None)
            
        player = table.round.current_player
        inp = input(f"{player.id}: ")

        if inp in actiondict.keys():
            args = actiondict[inp],
        elif inp.startswith('raise '):
            raise_by = inp.split()[1]
            args = PlayerAction.RAISE, raise_by
        else:
            continue

        table.round.privateIn(player.id, *args)


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

from abc import ABC
from copy import copy as shallowcopy

from ._round import AbstractRound, Round
from .enums import *
from .exceptions import *


# Table assumes added players have enough funds to join.
# This should be taken care when Player is created from
# User, before joining a table. 

class AbstractTable(ABC):
    RoundClass = AbstractRound

    def __init__(
        self, _id, seats, players,
        buyin, small_blind, big_blind
    ):
        self.id = _id
        self.seats = seats
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.buyin = buyin
        self.button = 0
        self.round = None
    
    @property
    def nplayers(self):
        return len(self.players)

    def __repr__(self):
        return f'Table({self.players})'

    def __bool__(self):
        return 2 <= self.nplayers <= self.seats
    
    def __eq__(self, other):
        return self.id == other.id

    def __contains__(self, player):
        for p in self.players: 
            if player.id == p.id: return True
        return False

    def __iter__(self):
        return iter(self.players)
    
    def __iadd__(self, players):
        for player in players: self._addPlayer(player)
        return self

    def __isub__(self, players):
        for player in players: self._removePlayer(player)
        return self
    
    def _shiftButton(self):
        self.button = (self.button + 1) % self.nplayers
    
    # kick out any player that has no money and 
    # cannot get any from the current round played
    def _kickoutLosers(self):
        for p in self.players:
            if p.money == 0 and (p.stake == 0 or p.is_folded): 
                self._removePlayer(p)
    
    def _addPlayer(self, player):
        self.players.append(player)
        self.publicOut(
            TablePublicOutId.PLAYERJOINED,
            player_id = player.id
        )

    def _removePlayer(self, player):
        self.players.remove([player])

        # if player is inside round, forcefold hand
        if player in self.round.players:
            if player.id == self.round.current_player.id:
                self.round.publicIn(
                    player.id, RoundPublicInId.FOLD
                )
            else: player.is_folded = True

        self.publicOut(
            TablePublicOutId.PLAYERREMOVED, 
            player_id = player.id
        )    
    
    def _newRound(self, round_id):
        self.round = self.RoundClass(
            round_id,
            shallowcopy(self.players),
            self.button,
            self.small_blind,
            self.big_blind
        )

    def _startRound(self, round_id):
        self._kickoutLosers()
        self._shiftButton()
        self._newRound(round_id)
        self.publicOut(
            TablePublicOutId.NEWROUNDSTARTED,
            round_id = round_id
        )
    
    def publicIn(self, player_id, action, **kwargs):
        """Override public in, to match the round's implementation"""
        ...
        
    def privateOut(self, player_id, out_id, **kwargs):
        """Override player out implementation"""
        # can be used to store additional table attributes
        ...

    def publicOut(self, out_id, **kwargs):
        """Override game out implementation"""
        # can be used to store additional table attributes
        ...

# add validators to the table operations
class ValidatedTable(AbstractTable):

    def _validatePlayer(self, player):
        if player.money < self.buyin:
            raise PlayerCannotJoinTable(
                player.id, self.id, 'Buyin is too low'
            )
        elif self.nplayers >= self.seats:
            raise PlayerCannotJoinTable(
                player.id, self.id, 'Table is full'
            )
        elif player in self:
            raise PlayerCannotJoinTable(
                player.id, self.id, 'Player already in table'
            )

    def _validateRoundCreation(self):
        if self.round: raise TableError('Round in progress')
        if not self: raise TableError('Table insufficient')

    def __init__(self, _id, seats, players, *args):
        player_sprite = type(players)([])
        super().__init__(_id, seats, player_sprite, *args)
        for player in players: self._addPlayer(player)

    def _addPlayer(self, player):
        self._kickoutLosers()
        self._validatePlayer(player)
        super()._addPlayer(player)

    def _startRound(self, round_id):
        self._validateRoundCreation()
        super()._startRound(round_id)

class Table(ValidatedTable):
    RoundClass = Round
    
    def _forceOutRoundQueue(self):
        for mes in self.round.private_out_queue: 
            self.privateOut(mes.player_id, mes.id, **mes.data)
        for mes in self.round.public_out_queue: 
            self.publicOut(mes.id, **mes.data)
        self.round.private_out_queue.clear()
        self.round.public_out_queue.clear()
    
    def publicIn(self, player_id, action, **kwargs):

        if action in RoundPublicInId:
            if not self.round: 
                return self.publicOut(
                    TablePublicOutId.ROUNDNOTINITIALIZED)
            else: self.round.publicIn(player_id, action, **kwargs)

        elif action in TablePublicInId:
            if action is TablePublicInId.STARTROUND: 
                self._startRound(1)
        
        # has to be done after every publicIn call
        self._forceOutRoundQueue()
        self._kickoutLosers()

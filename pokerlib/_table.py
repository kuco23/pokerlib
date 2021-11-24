from abc import ABC
from copy import copy as shallowcopy

from ._round import AbstractRound, Round
from ._player import PlayerGroup
from .enums import *
from .exceptions import *


# Table assums added players have enough funds to join.
# This should be taken care when Player is created from
# User, when joining a table. 

class AbstractTable(ABC):
    RoundClass = AbstractRound

    def __init__(
        self, _id, seats, buyin, 
        small_blind, big_blind
    ):
        self.id = _id
        self.seats = seats
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.buyin = buyin
        self.button = 0
        self.round = None
        self.players = PlayerGroup([])
    
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
    
    def _kickoutLosers(self):
        self.players = PlayerGroup(filter(
            lambda p: p.money > 0, self.players
        ))
    
    def _addPlayer(self, player):
        self.players.append(player)
        self.publicOut(
            TablePublicOutId.PLAYERJOINED,
            player_id = player.id
        )

    def _removePlayer(self, player):
        self.players.remove(player)

        # if player is inside round, removal has to be done 
        # by forcefolding
        if player in self.round.players:
            if player.id == self.round.current_player.id:
                self.round.publicIn(
                    player.id, RoundPublicInId.FOLD
                )
            else: player.is_folded = True

        self.publicOut(
            TablePublicOutId.PLAYERLEFT, 
            player_id = player.id
        )    
    
    def _newRound(self, round_id):
        self.round = self.Round(
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

# add checking to the table operations
class SafeTable(AbstractTable):
    
    def _addPlayer(self, player):
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
        super()._addPlayer(player)

    def _startRound(self, round_id):
        if self.round: raise TableError('Round in progress')
        self._kickoutLosers()
        if not self: raise TableError('Table insufficient')
        super()._startRound(round_id)

class Table(SafeTable):
    Round = Round

    def _popRoundOutQueue(self):
        private_out_queue = self.round.private_out_queue.copy()
        public_out_queue = self.round.public_out_queue.copy()
        self.round.private_out_queue.clear()
        self.round.public_out_queue.clear()
        return private_out_queue, public_out_queue
    
    def publicIn(self, player_id, action, **kwargs):

        if action in RoundPublicInId:
            self.round.publicIn(player_id, action, **kwargs)
            prv, pub = self._popRoundOutQueue()
            for mes in prv: 
                self.privateOut(mes.player_id, mes.id, **mes.data)
            for mes in pub: 
                self.publicOut(mes.id, **mes.data)

        elif action in TablePublicInId:
            if action is TablePublicInId.STARTROUND: 
                self._startRound(1)

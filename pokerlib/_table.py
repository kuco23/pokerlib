from abc import ABC
from copy import copy as shallowcopy

from ._round import AbstractRound, Round
from .enums import *


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
        return player in self.players

    def __getitem__(self, player_id):
        for p in self.players:
            if player_id == p.id: return p
        if self.round: 
            return self.round[player_id]

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

        # if player is inside an active round: forcefold
        if self.round and player in self.round:
            if player.id == self.round.current_player.id:
                self.round.publicIn(
                    player.id, RoundPublicInId.FOLD
                )
            else: 
                player.is_folded = True
                self.round._processState()

        self.publicOut(
            TablePublicOutId.PLAYERREMOVED, 
            player_id = player.id,
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

    def __init__(
        self, _id, seats, players, 
        buyin, small_blind, big_blind
    ):
        player_sprite = type(players)([])
        super().__init__(
            _id, seats, player_sprite, 
            buyin, small_blind, big_blind
        )
        for player in players: self._addPlayer(player)

    def _addPlayer(self, player):
        self._kickoutLosers()
        if player.money < self.buyin: self.privateOut(
            player.id, TablePrivateOutId.BUYINTOOLOW, 
            table_id=self.id)
        elif self.nplayers >= self.seats: self.privateOut(
            player.id, TablePrivateOutId.TABLEFULL, 
            table_id=self.id)
        elif player in self: self.privateOut(
            player.id, TablePrivateOutId.PLAYERALREADYATTABLE,
            table_id=self.id)
        else: super()._addPlayer(player)

    def _startRound(self, round_id):
        if self.round: self.publicOut(
            TablePublicOutId.ROUNDINPROGRESS, 
            round_id=round_id, table_id=self.id)
        elif not self: self.publicOut(
            TablePublicOutId.INCORRECTNUMBEROFPLAYERS,
            round_id=round_id, table_id=self.id)
        else: super()._startRound(round_id)

class Table(ValidatedTable):
    RoundClass = Round
    
    def _forceOutRoundQueue(self):
        if self.round is None: return
        for msg in self.round.private_out_queue: 
            self.privateOut(msg.player_id, msg.id, **msg.data)
        for msg in self.round.public_out_queue: 
            self.publicOut(msg.id, **msg.data)
        self.round.private_out_queue.clear()
        self.round.public_out_queue.clear()
    
    def publicIn(self, player_id, action, **kwargs):

        if action in RoundPublicInId:
            if not self.round: self.publicOut(
                TablePublicOutId.ROUNDNOTINITIALIZED)
            else: self.round.publicIn(
                player_id, action, kwargs.get('raise_by'))

        elif action in TablePublicInId:
            if action is TablePublicInId.STARTROUND: 
                self._startRound(kwargs.get('round_id'))
            elif action is TablePublicInId.LEAVETABLE:
                player = self.players.getPlayerById(player_id)
                self._removePlayer(player)
            elif action is TablePublicInId.BUYIN:
                self += [kwargs['player']]

        # has to be done after every publicIn call
        self._forceOutRoundQueue()
        self._kickoutLosers()

from operator import add
from math import inf

from .enums import *
from ._player import Player, PlayerGroup
from ._round import Round

class Table:
    Round = Round

    def __init__(self, _id, players, small_blind, big_blind):
        self.id = _id
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.players = players
        self.button = 0
        self.round = None
        self.interrupt = False
        self.__player_removal_schedule = []
        self.__player_addition_schedule = []

    def __bool__(self):
        return 2 <= len(self.players.getNotBrokePlayers()) <= 9

    def __contains__(self, _id):
        return self.all_players.getPlayerById(_id) is not None

    def __eq__(self, other):
        return self.id == other.id
    
    def __iadd__(self, players):
        self.__player_addition_schedule.extend(players)
        if not self.round: self._updatePlayers()
        return self

    def __isub__(self, players):
        self.__player_removal_schedule.extend(players)
        if not self.round: self._updatePlayers()
        else:
            for player in players:
                if player.id == self.round.current_player.id:
                    self.round.processAction(PlayerAction.FOLD)
                elif player.id in self.round:
                    player.is_folded = True
        return self
                    
    @property
    def all_players(self):
        return add(
            self.players,
            self.__player_addition_schedule
        )

    # called only when round is finished
    def _updatePlayers(self):
        self.players.extend(self.__player_addition_schedule)
        self.players.remove(self.__player_removal_schedule)
        self.__player_addition_schedule.clear()
        self.__player_removal_schedule.clear()

    def newRound(self, round_id):
        assert not self.round
        
        self._updatePlayers()
        assert self

        round_players = self.players.getNotBrokePlayers()
        self.button = (self.button + 1) % len(round_players)
        self.round = self.Round(
            round_id,
            round_players,
            self.button,
            self.small_blind,
            self.big_blind
        )

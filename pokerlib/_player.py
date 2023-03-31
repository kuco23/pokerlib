class Player:

    def __init__(self, table_id, _id, name, money):
        self.table_id = table_id
        self.id = _id
        self.name = name
        self.money = money

        self.cards = tuple()
        self.hand = None
        self.is_folded = False
        self.is_all_in = False

        self.stake = 0
        self.turn_stake = [0, 0, 0, 0]

        self.played_turn = False

    @property
    def is_active(self):
        return not (self.is_folded or self.is_all_in)

    def __repr__(self):
        return f"Player({self.name}, {self.money})"

    def __str__(self):
        return str(self.name)

    def __lt__(self, other):
        return self.hand < other.hand

    def __gt__(self, other):
        return self.hand > other.hand

    def __eq__(self, other):
        return self.hand == other.hand

    def resetState(self):
        self.cards = tuple()
        self.hand = None
        self.is_folded = False
        self.is_all_in = False
        self.stake = 0
        self.turn_stake = [0, 0, 0, 0]
        self.played_turn = False


class PlayerGroup(list):

    def __contains__(self, player):
        for p in self:
            if p.id == player.id:
                return True
        return False

    def __getitem__(self, i):
        ret = super().__getitem__(i)
        isl = isinstance(ret, list)
        return type(self)(ret) if isl else ret

    def __add__(self, other):
        return type(self)(super().__add__(other))

    def remove(self, players):
        removal_ids = list(map(lambda x: x.id, players))
        self[:] = type(self)(filter(
            lambda player: player.id not in removal_ids,
            self
        ))

    def getPlayerById(self, _id):
        for player in self:
            if player.id == _id:
                return player

    def getPlayerByAttr(self, attr, val):
        for player in self:
            if getattr(player, attr) == val:
                return player

    def previousActivePlayer(self, i):
        j = self.previousActiveIndex(i)
        return self[j]

    def nextActivePlayer(self, i):
        j = self.nextActiveIndex(i)
        return self[j]

    def previousActiveIndex(self, i):
        n = len(self)
        rn = reversed(range(i + 1, i + n))
        for k in map(lambda j: j % n, rn):
            if self[k].is_active: return k

    def nextActiveIndex(self, i):
        n = len(self)
        rn = range(i + 1, i + n)
        for k in map(lambda j: j % n, rn):
            if self[k].is_active: return k

    def getActivePlayers(self):
        return type(self)(filter(
            lambda player: player.is_active,
            self
        ))

    def getNotFoldedPlayers(self):
        return type(self)(filter(
            lambda player: not player.is_folded,
            self
        ))

    def getPlayersWithLessMoney(self, money):
        return type(self)(filter(
            lambda player: player.money <= money,
            self
        ))

    def getPlayersWithMoreMoney(self, money):
        return type(self)(filter(
            lambda player: player.money >= money,
            self
        ))

    def allPlayedTurn(self):
        for player in self:
            if not player.played_turn and player.is_active:
                return False
        return True

    def winners(self):
        winner = max(self)
        return type(self)(
            [player for player in self if player == winner]
        )


class PlayerSeats(list):
    def __contains__(self, player):
        for p in self:
            if p is not None and p.id == player.id:
                return True
        return False

    def seat_place(self, player, ind: int) -> bool:
        if ind < len(self) and self[ind] is None:
            self[ind] = player
            return True
        return False

    def remove(self, players):
        removal_ids = set(map(lambda x: x.id, players))
        for i in range(len(self)):
            p = super().__getitem__(i)
            if p is not None and p.id in removal_ids:
                self[i] = None

    def append(self, __object: Player):
        for i in range(len(self)):
            p = super().__getitem__(i)
            if p is None:
                self[i] = __object
                return i

    def __iter__(self):
        for p in super().__iter__():
            if p is not None:
                yield p

    def seats(self):
        return super().__iter__()

    def get_players_group(self) -> PlayerGroup:
        return PlayerGroup(filter(
            lambda player: player is not None,
            self
        ))

    def __add__(self, other):
        copy = type(self)(super().__add__([]))
        for p in other:
            copy.append(p)
        return copy

    def getPlayerById(self, _id):
        for player in self:
            if player.id == _id:
                return player
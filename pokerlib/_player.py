from operator import add

class Player:

    def __init__(self, table_id, _id, name, money):
        self.table_id = table_id
        self.id = _id
        self.name = name
        self.money = money
        self.cards = tuple()
        self.hand = None
        self.group_kickers = None
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

    def __eq__(self, other):
        return self.id == other.id

    def resetState(self):
        self.cards = tuple()
        self.hand = None
        self.group_kickers = None
        self.is_folded = False
        self.is_all_in = False
        self.stake = 0
        self.turn_stake = [0, 0, 0, 0]
        self.played_turn = False


class PlayerGroup(list):

    def __getitem__(self, i):
        is_slice = isinstance(i, slice)
        ret = super().__getitem__(i if is_slice else i % len(self))
        return type(self)(ret) if is_slice else ret

    def __add__(self, other):
        return type(self)(super().__add__(other))

    def countActivePlayers(self):
        counter = 0
        for player in self:
            if player.is_active:
                counter += 1
        return counter

    def countUnfoldedPlayers(self):
        counter = 0
        for player in self:
            if not player.is_folded:
                counter += 1
        return counter

    def getPlayerById(self, _id):
        for player in self:
            if player.id == _id:
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

    def nextUnfoldedIndex(self, i):
        n = len(self)
        rn = range(i + 1, i + n)
        for k in map(lambda j: j % n, rn):
            if not self[k].is_folded: return k

    def previousUnfoldedIndex(self, i):
        n = len(self)
        rn = reversed(range(i + 1, i + n))
        for k in map(lambda j: j % n, rn):
            if not self[k].is_folded: return k

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

    def allPlayedTurn(self):
        for player in self:
            if not player.played_turn and player.is_active:
                return False
        return True

    def winners(self):
        winner = max(self, key=lambda x: x.hand)
        return type(self)(
            [player for player in self if player.hand == winner.hand]
        )

    def sortedByWinningAmountProspect(self):
        return type(self)(add(
            sorted(
                [player for player in self if player.is_all_in],
                key = lambda player: player.stake
            ),
            sorted(
                [player for player in self if player.is_active],
                key = lambda player: player.stake
            )
        ))


class PlayerSeats(list):

    def __add__(self, other):
        copy = type(self)(super().__add__([]))
        for p in other:
            copy.append(p)
        return copy

    def __getitem__(self, i):
        ret = super().__getitem__(i)
        isl = isinstance(ret, list)
        return type(self)(ret) if isl else ret

    def __iter__(self):
        for p in super().__iter__():
            if p is not None:
                yield p

    def __contains__(self, player):
        for p in self:
            if p.id == player.id:
                return True
        return False

    def seats(self):
        return super().__iter__()

    def nFilled(self):
        n = 0
        for p in self:
            if p is not None:
                n += 1
        return n

    def seatFree(self, ind: int) -> bool:
        return 0 <= ind < len(self) and self[ind] is None

    def seatPlayerAt(self, player, ind: int) -> bool:
        if self.seatFree(ind):
            self[ind] = player
            return True
        return False

    def remove(self, player):
        for i, p in enumerate(super().__iter__()):
            if p is not None and p == player:
                self[i] = None

    def append(self, player: Player):
        for i, p in enumerate(super().__iter__()):
            if p is None:
                self[i] = player
                return i

    def getPlayerGroup(self) -> PlayerGroup:
        return PlayerGroup(filter(
            lambda player: player is not None,
            self
        ))

    def getPlayerById(self, _id):
        for player in self:
            if player.id == _id:
                return player
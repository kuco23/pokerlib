from bisect import insort
from .enums import Hand, Suit, Rank

def reactiveParse(fun):
    def modfun(self, *args, **kwargs):
        if not self._parsed:
            self.parse()
            self._parsed = True
        return fun(self, *args, **kwargs)
    return modfun

class HandParser:
    __slots__ = [
        "original", "ncards", "cards",
        "_handenum", "_handbase", "_kickers",
        "_parsed",
        "_ranknums", "_suitnums",
        "_flushsuit", "_straightindices"
    ]

    def __init__(self, cards: list):
        self._parsed = False

        self.original = cards
        self.ncards = len(cards)
        self.cards = sorted(cards, key = lambda x: x[0])

        self._handenum = None
        self._handbase = []
        self._kickers = []

        self._ranknums = [0] * 13
        self._suitnums = [0] * 4
        for rank, suit in cards:
            self._ranknums[rank] += 1
            self._suitnums[suit] += 1

        self._flushsuit = None
        for suit in Suit:
            if self._suitnums[suit] >= 5:
                self._flushsuit = suit
                break

        self._straightindices = None

    @property
    @reactiveParse
    def handenum(self):
        return self._handenum

    @property
    @reactiveParse
    def handbase(self):
        return self._handbase

    @property
    @reactiveParse
    def kickers(self):
        return self._kickers

    @property
    def handbasecards(self):
        return map(
            lambda i: self.cards[i],
            self.handbase
        )
    @property
    def kickercards(self):
        return map(
            lambda i: self.cards[i],
            self.kickers
        )
    @property
    def handfullcards(self):
        return map(
            lambda i: self.cards[i],
            self.handbase + self.kickers
        )

    def __str__(self):
        return str(self.cards)

    def __repr__(self):
        return f"HandParser({self.cards})"

    def __eq__(self, other):
        if self.handenum != other.handenum: return False
        for (s_val, _), (o_val, _) in zip(self.handfullcards,
                                          other.handfullcards):
            if s_val != o_val: return False
        return True

    def __gt__(self, other):
        if self.handenum != other.handenum:
            return self.handenum > other.handenum
        for (s_val, _), (o_val, _) in zip(self.handfullcards,
                                          other.handfullcards):
            if s_val != o_val: return s_val > o_val
        return False

    def __lt__(self, other):
        if self.handenum != other.handenum:
            return self.handenum < other.handenum
        for (s_val, _), (o_val, _) in zip(self.handfullcards,
                                          other.handfullcards):
            if s_val != o_val: return s_val < o_val
        return False

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return not other > self

    def __iadd__(self, cards):
        if len(cards) > 0:
            self._addCards(cards)
        return self

    def _addCards(self, cards):
        self._parsed = False
        self.original.extend(cards)
        self.ncards += len(cards)
        for card in cards: insort(self.cards, card)

        self._handenum = None
        self._handbase.clear()
        self._kickers.clear()

        for rank, suit in cards:
            self._ranknums[rank] += 1
            self._suitnums[suit] += 1

        for suit in Suit:
            if self._suitnums[suit] >= 5:
                self._flushsuit = suit
                break

    @staticmethod
    def _getStraightIndices(valnums):
        straightindices = [None] * 5
        straightlen, indexptr = 1, sum(valnums)
        for i in reversed(range(len(valnums))):
            indexptr -= valnums[i]
            if valnums[i-1] and valnums[i]:
                straightindices[straightlen-1] = indexptr
                straightlen += 1
                if straightlen == 5:
                    if indexptr == 0:
                        indexptr = sum(valnums)-1
                    else: indexptr -= valnums[i-1]
                    straightindices[4] = indexptr
                    return straightindices
            else: straightlen = 1

    def _setStraightFlush(self):
        counter = 0
        suited_vals, permut = [0] * 13, [0] * len(self.cards)
        for i, (val, suit) in enumerate(self.cards):
             if suit == self._flushsuit:
                 suited_vals[val] += 1
                 permut[counter] = i
                 counter += 1

        suited_handbase = self._getStraightIndices(suited_vals)
        if suited_handbase is not None:
            self._handenum = Hand.STRAIGHTFLUSH
            self._handbase = [permut[i] for i in suited_handbase]
            return True

        return False

    def _setFourOfAKind(self):
        self._handenum = Hand.FOUROFAKIND

        hindex = -1
        for valnum in self._ranknums:
            hindex += valnum
            if valnum == 4: break

        self._handbase = [hindex, hindex-1, hindex-2, hindex-3]

    def _setFullHouse(self):
        self._handenum = Hand.FULLHOUSE

        threes, twos = None, None
        hindex = self.ncards
        for valnum in reversed(self._ranknums):
            hindex -= valnum
            if valnum == 3 and threes is None:
                threes = hindex
                if twos is not None: break
            elif valnum >= 2 and twos is None:
                twos = hindex
                if threes is not None: break

        self._handbase = [threes, threes+1, threes+2, twos, twos+1]

    def _setFlush(self):
        self._handenum = Hand.FLUSH
        self._handbase = [0] * 5

        counter = 0
        for i in reversed(range(self.ncards)):
            if self.cards[i][1] == self._flushsuit:
                self._handbase[counter] = i
                counter += 1
                if counter == 5: break

    def _setStraight(self):
        self._handenum = Hand.STRAIGHT
        self._handbase = self._straightindices

    def _setThreeOfAKind(self):
        self._handenum = Hand.THREEOFAKIND

        hindex = -1
        for valnum in self._ranknums:
            hindex += valnum
            if valnum == 3: break

        self._handbase = [hindex, hindex-1, hindex-2]

    def _setTwoPair(self):
        self._handenum = Hand.TWOPAIR
        self._handbase.clear()

        hindex, paircounter = self.ncards, 0
        for valnum in reversed(self._ranknums):
            hindex -= valnum
            if valnum == 2:
                self._handbase.extend([hindex+1, hindex])
                paircounter += 1
                if paircounter == 2: break

    def _setOnePair(self):
        self._handenum = Hand.ONEPAIR

        hindex = -1
        for valnum in self._ranknums:
            hindex += valnum
            if valnum == 2: break

        self._handbase = [hindex, hindex-1]

    def _setHighCard(self):
        self._handenum = Hand.HIGHCARD
        self._handbase = [self.ncards - 1]

    def _setHand(self):
        self._straightindices = self._getStraightIndices(
            self._ranknums)

        pairnums = [0] * 5
        for num in self._ranknums: pairnums[num] += 1

        if self._straightindices is not None \
            and self._flushsuit is not None \
            and self._setStraightFlush(): pass
        elif pairnums[4]:
            self._setFourOfAKind()
        elif pairnums[3] == 2 or pairnums[3] == 1 and pairnums[2] >= 1:
            self._setFullHouse()
        elif self._flushsuit is not None:
            self._setFlush()
        elif self._straightindices is not None:
            self._setStraight()
        elif pairnums[3]:
            self._setThreeOfAKind()
        elif pairnums[2] >= 2:
            self._setTwoPair()
        elif pairnums[2] == 1:
            self._setOnePair()
        elif pairnums[1] >= 1:
            self._setHighCard()

    def _setKickers(self):
        self._kickers.clear()

        inhand = [False] * self.ncards
        for i in self._handbase: inhand[i] = True

        i, lim = self.ncards - 1, 5 - len(self._handbase)
        while len(self._kickers) < lim and i >= 0:
            if not inhand[i]: self._kickers.append(i)
            i -= 1

    # with introduction of reactive parsing, this method should
    # be treated privately, but renaming parse to _parse would
    # change the class interface
    def parse(self):
        self._setHand()
        self._setKickers()
        self._parsed = True


class HandParserGroup(list):

    def __repr__(self):
        return f"HandParserGroup{super().__repr__()}"

    def getGroupKicker(self):
        winner = max(self)
        hands = [hand for hand in self if hand.handenum == winner.handenum]
        for i in range(len(winner.kickers)):
            for hand in hands:
                hki, wki = hand.kickers[i], winner.kickers[i]
                hri, wri = hand.cards[hki][0], winner.cards[wki][0]
                if hri < wri: return wri
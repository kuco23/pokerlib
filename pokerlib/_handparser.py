from bisect import insort
from .enums import Hand, Value, Suit

class HandParser:
    __slots__ = [
        "original", "ncards", "cards",
        "handenum", "handbase", "kickers",
        "__valnums", "__suitnums",
        "__flushsuit", "__straightindexes"
    ]

    def __init__(self, cards: list):
        self.original = cards
        self.ncards = len(cards)
        self.cards = sorted(cards, key = lambda x: x[0])

        self.handenum = None
        self.handbase = []
        self.kickers = []

        self.__valnums = [0] * 13
        self.__suitnums = [0] * 4
        for value, suit in cards:
            self.__valnums[value] += 1
            self.__suitnums[suit] += 1

        self.__flushsuit = None
        for suit in Suit:
            if self.__suitnums[suit] >= 5:
                self.__flushsuit = suit
                break

        self.__straightindexes = \
            self.getStraightIndexes(self.__valnums)

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
            self.handbase + self.kickers
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

    def addCards(self, cards):
        self.original.extend(cards)
        self.ncards += len(cards)
        for card in cards: insort(self.cards, card)

        self.handenum = None
        self.handbase.clear()
        self.kickers.clear()

        for value, suit in cards:
            self.__valnums[value] += 1
            self.__suitnums[suit] += 1

        for suit in Suit:
            if self.__suitnums[suit] >= 5:
                self.__flushsuit = suit
                break

        self.__straightindexes = \
            self.getStraightIndexes(self.__valnums)

    @staticmethod
    def getStraightIndexes(valnums):
        straightindexes = [None] * 5
        straightlen, indexptr = 1, sum(valnums)
        for i in reversed(range(len(valnums))):
            indexptr -= valnums[i]
            if valnums[i-1] and valnums[i]:
                straightindexes[straightlen-1] = indexptr
                straightlen += 1
                if straightlen == 5:
                    if indexptr == 0:
                        indexptr = sum(valnums)-1
                    else: indexptr -= valnums[i-1]
                    straightindexes[4] = indexptr
                    return straightindexes
            else: straightlen = 1

    def _setStraightFlush(self):
        counter = 0
        suited_vals, permut = [0] * 13, [0] * len(self.cards)
        for i, (val, suit) in enumerate(self.cards):
             if suit == self.__flushsuit:
                 suited_vals[val] += 1
                 permut[counter] = i
                 counter += 1

        suited_handbase = self.getStraightIndexes(suited_vals)
        if suited_handbase is not None:
            self.handenum = Hand.STRAIGHTFLUSH
            self.handbase = [permut[i] for i in suited_handbase]
            return True

        return False

    def _setFourOfAKind(self):
        self.handenum = Hand.FOUROFAKIND

        hindex = -1
        for valnum in self.__valnums:
            hindex += valnum
            if valnum == 4: break

        self.handbase = [hindex, hindex-1, hindex-2, hindex-3]

    def _setFullHouse(self):
        self.handenum = Hand.FULLHOUSE

        threes, twos = [], []
        hindex = -1
        for val, valnum in enumerate(self.__valnums):
            hindex += valnum
            if valnum == 3: threes.append((val, hindex))
            elif valnum == 2: twos.append((val, hindex))

        i1, i2 = [threes.pop()[1], max(threes + twos)[1]]
        self.handbase = [i1, i1-1, i1-2, i2, i2-1]

    def _setFlush(self):
        self.handenum = Hand.FLUSH
        self.handbase.clear()

        counter = 0
        for i in reversed(range(self.ncards)):
            if self.cards[i][1] == self.__flushsuit:
                self.handbase.append(i)
                counter += 1
            if counter == 5:
                break

    def _setStraight(self):
        self.handenum = Hand.STRAIGHT
        self.handbase = self.__straightindexes

    def _setThreeOfAKind(self):
        self.handenum = Hand.THREEOFAKIND
        self.handbase.clear()

        hindex = -1
        for valnum in self.__valnums:
            hindex += valnum
            if valnum == 3: break

        self.handbase = [hindex, hindex-1, hindex-2]

    def _setTwoPair(self):
        self.handenum = Hand.TWOPAIR
        self.handbase.clear()

        hindex, paircounter = self.ncards, 0
        for valnum in reversed(self.__valnums):
            hindex -= valnum
            if valnum == 2:
                self.handbase.extend([hindex+1, hindex])
                paircounter += 1
                if paircounter == 2: break

    def _setOnePair(self):
        self.handenum = Hand.ONEPAIR

        hindex = -1
        for valnum in self.__valnums:
            hindex += valnum
            if valnum == 2: break

        self.handbase = [hindex, hindex-1]

    def _setHighCard(self):
        self.handenum = Hand.HIGHCARD
        self.handbase = [self.ncards - 1]

    def _setHand(self):
        pairnums = [0] * 5
        for num in self.__valnums: pairnums[num] += 1

        if None not in [self.__straightindexes, self.__flushsuit] \
        and self._setStraightFlush():
            pass
        elif pairnums[4]:
            self._setFourOfAKind()
        elif pairnums[3] == 2 or pairnums[3] == 1 and pairnums[2] >= 1:
            self._setFullHouse()
        elif self.__flushsuit is not None:
            self._setFlush()
        elif self.__straightindexes is not None:
            self._setStraight()
        elif pairnums[3]:
            self._setThreeOfAKind()
        elif pairnums[2] >= 2:
            self._setTwoPair()
        elif pairnums[2] == 1:
            self._setOnePair()
        else:
            self._setHighCard()

    def _setKickers(self):
        self.kickers.clear()
        
        inhand = [False] * self.ncards
        for i in self.handbase: inhand[i] = True
        
        i, lim = self.ncards - 1, 5 - len(self.handbase)
        while len(self.kickers) < lim and i >= 0:
            if not inhand[i]: self.kickers.append(i)
            i -= 1

    def parse(self):
        self._setHand()
        self._setKickers()


class HandParserGroup(list):

    def __repr__(self):
        return f"HandParserGroup{self}"

    def getGroupKickers(self):
        win = max(self)
        los = [hand for hand in self if hand < win]
        if not los: return []
        
        mlos = max(los)
        if win.handenum != mlos.handenum: return []
        
        w_base, w_kick, ml_base, ml_kick = map(
            lambda cards: next(zip(*cards)),
            (win.handbasecards, win.kickercards,
             mlos.handbasecards, mlos.kickercards)
        )

        fivebased = [
            Hand.STRAIGHT,
            Hand.FLUSH,
            Hand.FULLHOUSE,
            Hand.STRAIGHTFLUSH
        ]
                     
        if win.handenum not in fivebased:
            if w_base != ml_base: return []
            else: kicker_search = zip(w_kick, ml_kick)

        elif win.handenum == Hand.FLUSH:
            if w_base[0] != ml_base[0]: return []
            kicker_search = zip(w_base[1:], ml_base[1:])

        else: return []

        kickers = []
        for w_val, l_val in kicker_search:
            kickers.append(w_val)
            if w_val > l_val: return kickers

        return []

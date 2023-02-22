import sys
sys.path.append('../pokerlib')

from pokerlib import HandParser, HandParserGroup
from pokerlib.enums import Rank, Suit, Hand

CARDS = [[rank, suit] for rank in Rank for suit in Suit]

cards1 = [[3,2], [4,1], [6,0], [8,1], [10,2], [11,3], [12,0]]
hand1 = HandParser(cards1)
assert hand1.handenum == Hand.HIGHCARD
assert hand1.handbase == [6]
assert hand1.kickers == [5,4,3,2]

cards2 = [[1,1], [1,0], [2,2], [4,1], [10,2], [11,3], [12,2]]
hand2 = HandParser(cards2)
assert hand2.handenum == Hand.ONEPAIR
assert hand2.handbase == [1,0]
assert hand2.kickers == [6,5,4]

cards3 = [[2,0], [3,0], [4,0], [10,1], [10,2], [11,1], [11,3]]
hand3 = HandParser(cards3)
assert hand3.handenum == Hand.TWOPAIR
assert hand3.handbase == [6,5,4,3]
assert hand3.kickers == [2]

cards4 = [[0,0], [0,1], [0,2], [1,2], [2,3], [3,3], [7,1]]
hand4 = HandParser(cards4)
assert hand4.handenum == Hand.THREEOFAKIND
assert hand4.handbase == [2,1,0]
assert hand4.kickers == [6,5]

cards5 = [[3,0], [3,3], [4,2], [5,3], [6,1], [7,1], [12,2]]
hand5 = HandParser(cards5)
assert hand5.handenum == Hand.STRAIGHT
assert hand5.handbase == [5,4,3,2,0]
assert hand5.kickers == []

cards6 = [[4,2], [6,2], [8,2], [8,1], [8,3], [10,2], [12,2]]
hand6 = HandParser(cards6)
assert hand6.handenum == Hand.FLUSH
assert hand6.handbase == [6,5,2,1,0]
assert hand6.kickers == []

cards7 = [[0,1], [2,2], [2,3], [5,1], [5,2], [5,3], [10,1]]
hand7 = HandParser(cards7)
assert hand7.handenum == Hand.FULLHOUSE
assert hand7.handbase == [3,4,5,1,2]
assert hand7.kickers == []

cards8 = [[3,1], [6,2], [6,3], [6,1], [6,0], [12,0], [12,1]]
hand8 = HandParser(cards8)
assert hand8.handenum == Hand.FOUROFAKIND
assert hand8.handbase == [4,3,2,1]
assert hand8.kickers == [6]

cards9 = [[3,2], [8,2], [9,2], [10,2], [11,1], [11,2], [12,2]]
hand9 = HandParser(cards9)
assert hand9.handenum == Hand.STRAIGHTFLUSH
assert hand9.handbase == [6,5,3,2,1]
assert hand9.kickers == []

base = [[4,0], [8,0], [1,0], [10,1], [12,1]]
c1 = [[12,2],[5,2]]
c2 = [[2,3], [4,3]]
c3 = [[12,0], [9,2]]
h1,h2,h3 = map(lambda c: HandParser(base + c), [c1, c2, c3])
handgroup = HandParserGroup([h1,h2,h3])
kickers = handgroup.getGroupKicker()
assert kickers == 9

cards10 = [[3,1], [6,2], [6,3], [6,1], [6,0], [12,0], [12,1]]
hand10 = HandParser(cards10)
assert hand10._parsed == False
assert hand10.handenum == Hand.FOUROFAKIND
assert hand10._parsed == True
# check that parsed() was not called
hand10._handbase = []
assert hand10.handbase == []
# force-parse
hand10.parse()
assert hand10.handbase == [4,3,2,1]

cards11 = [[3,1], [6,2], [6,3], [6,1], [6,0], [12,0], [12,1]]
hand11 = HandParser(cards11)
assert list(hand11.handbasecards) == [[6, 0], [6, 1], [6, 3], [6, 2]]

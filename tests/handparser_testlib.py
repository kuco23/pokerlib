from sys import path
from pathlib import Path
path.append(str(Path().cwd().parent))
from random import sample
from timeit import timeit

from pokerlib import HandParser, HandParserGroup
from pokerlib.enums import Value, Suit

SUITS = ['♠', '♣', '♦', '♥']
CARDS = [[val, suit] for val in Value for suit in Suit]

def reprHand(hand):
    print(', '.join(
        [str(int(val)) + SUITS[suit]
         for val, suit in hand.cards]
        ))

def reprHandGroup(hands):
    list(map(reprHand, hands))

def randomHand():
    hand = HandParser(sample(CARDS, 7))
    hand.parse()
    return hand

def randomHandGroup(n):
    l, cards = [], sample(CARDS, 5 + 2 * n)
    base = cards[:5]
    for i in range(n):
        l.append(HandParser(base + [cards[5+2*i], cards[5+2*i+1]]))
        l[i].parse()
    return HandParserGroup(l)

def randomHandTests():
    while True:
        hand = randomHand()
        reprHand(hand)
        input()

def timeParser(n):
    b = timeit(lambda: HandParser(sample(CARDS, 7)).parse(),
               number=n)
    a = timeit(lambda: sample(CARDS, 7), number=n)
    print(b - a)

base = [[4,0], [12,0], [1,0], [10,1], [12,1]]

c1 = [[2,2],[4,2]]
c2 = [[2,3], [4,3]]
c3 = [[11,0], [6,2]]
h1,h2,h3 = map(lambda c: HandParser(base + c), [c1,c2,c3])

g = HandParserGroup([h1,h2,h3])
g[0].parse()
g[1].parse()
g[2].parse()

g.getGroupKickers()

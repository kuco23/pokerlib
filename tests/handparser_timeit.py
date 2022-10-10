from sys import path
from pathlib import Path
from timeit import timeit
from random import sample
from itertools import product

path.append(str(Path().cwd().parent))
from pokerlib import HandParser
from pokerlib.enums import Rank, Suit

def randomParse():
    cards = sample(list(product(Rank, Suit)), 7)
    hand = HandParser(cards)
    hand.parse()

t = timeit(randomParse, number=10**6)
print(t)
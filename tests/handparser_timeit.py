import sys
sys.path.append('../pokerlib')

from timeit import timeit
from itertools import product
from random import sample
from pokerlib import HandParser
from pokerlib.enums import Rank, Suit

def randomHand():
    return sample(list(product(Rank, Suit)), 7)

def randomParse():
    HandParser(randomHand()).parse()

n = 10**6
thand = timeit(randomHand, number=n)
tparse = timeit(randomParse , number=n)
print(f'HandParser parse time: {tparse - thand}')
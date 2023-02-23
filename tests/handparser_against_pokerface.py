import sys
sys.path.append('../pokerlib')

from random import sample
from pokerlib import HandParser
from pokerlib.enums import Rank, Suit, Hand
from pokerface import StandardEvaluator, parse_cards

n_tests = 10000

POKERFACE_RANK = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
POKERFACE_SUIT = ['s', 'c', 'd', 'h']

POKERLIB_CARDS = [[rank, suit] for rank in Rank for suit in Suit]
POKERFACE_CARDS = [rank + suit for rank in POKERFACE_RANK for suit in POKERFACE_SUIT]

evaluator = StandardEvaluator()

def indexedPokerlibHand(seed):
    return HandParser([POKERLIB_CARDS[i] for i in seed])

def indexedPokerfaceHand(seed):
    cards = [POKERFACE_CARDS[i] for i in seed]
    return evaluator.evaluate_hand(
        parse_cards(''.join(cards[:2])),
        parse_cards(''.join(cards[2:])))

for i in range(n_tests):
    seed_1 = sample(range(len(POKERLIB_CARDS)), 7)
    seed_2 = sample(range(len(POKERLIB_CARDS)), 7)
    pokerlib_hand_1 = indexedPokerlibHand(seed_1)
    pokerlib_hand_2 = indexedPokerlibHand(seed_2)
    pokerface_hand_1 = indexedPokerfaceHand(seed_1)
    pokerface_hand_2 = indexedPokerfaceHand(seed_2)
    assert (pokerlib_hand_1 > pokerlib_hand_2) is (pokerface_hand_1 > pokerface_hand_2)
    assert (pokerlib_hand_1 < pokerlib_hand_2) is (pokerface_hand_1 < pokerface_hand_2)
    assert (pokerlib_hand_1 == pokerlib_hand_2) is (pokerface_hand_1 == pokerface_hand_2)
import sys
sys.path.append('../pokerlib')

from random import sample
from itertools import product
from pokerlib import HandParser
from pokerlib.enums import Rank, Suit

def winningProbability(players_cards, board=[], n=1000):
    cards = list(product(Rank, Suit))
    for card in board: cards.remove(card)
    for player_cards in players_cards:
        for card in player_cards:
            cards.remove(card)

    wins = [0] * len(players_cards)
    for i in range(n):
        board_ = sample(cards, 5-len(board))
        hands = [
            HandParser(player_cards + board + board_)
            for player_cards in players_cards
        ]
        winner = max(hands)
        for i, hand in enumerate(hands):
            if hand == winner: wins[i] += 1

    return [win / n for win in wins]

w1, w2 = winningProbability([
    [(Rank.ACE, Suit.HEART), (Rank.KING, Suit.HEART)],
    [(Rank.KING, Suit.SPADE), (Rank.KING, Suit.DIAMOND)]
])
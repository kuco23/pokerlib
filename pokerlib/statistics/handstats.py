from timeit import timeit
from random import shuffle, sample
from .._handparser import HandParser

class StatisticModel:
    __slots__ = ['hand', 'table']
    __deck = [[i, j] for j in range(4) for i in range(13)]

    def __init__(self, hand, table=[]):
        self.hand = hand
        self.table = table

    def simulate(self, nforeign, nsim):
        deck = self.__deck.copy()
        for card in self.hand + self.table:
            deck.remove(card)

        n_table = 5 - len(self.table)
        n_cards = n_table + 2 * nforeign
        
        p = 0
        for _ in range(nsim):
            deckit = iter(sample(deck, n_cards))
            
            table_fill = [next(deckit) for _ in range(n_table)]
            table_filled = self.table + table_fill
            
            self_hand_full = HandParser(self.hand + table_filled)
            self_hand_full.parse()
            
            for _ in range(nforeign):
                foreign_hand = [next(deckit) for _ in range(2)]
                foreign_hand_full = HandParser(
                    foreign_hand + table_filled
                )
                foreign_hand_full.parse()
                
                if foreign_hand_full > self_hand_full:
                    break
                
            else: p += 1

        return p / nsim

if __name__ == '__main__':
    nforeign, nsim = 4, 10**3
    hand = [[12, 0], [12, 2]]
    table = [[5, 1], [6, 1], [7, 1]]
    
    model = StatisticModel(hand, table)
    p = model.simulate(nforeign, nsim)
    print(p)

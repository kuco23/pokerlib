# pokerlib
[![PyPI version](https://badge.fury.io/py/pokerlib.svg)](https://pypi.org/project/pokerlib)

A lightweight Python poker library that focuses on simplifying a poker game implementation
when its io is supplied. It includes modules that help with hand parsing and poker game continuation.

One application of this library was made by the PokerMessenger app,
which supplies library with io in the form of messenger group threads.
The app's repo is at https://github.com/kuco23/pokermessenger.

To install, run 
```bash
pip install pokerlib
```

## Usage
Library consists of a module for parsing cards, which can be used seperately, and modules that aid in running a poker game.

### HandParser
This module helps with parsing hands. A hand usually consists of 2 dealt cards plus 5 on the board, and `HandParser` is optimized to work with up to 7 cards (otherwise flushes and straights require some small additional work). A card is defined as a pair of two enums. All of the enums used are of `IntEnum` type, so you can also freely interchange them for integers. Below is an example of how to construct two different hands and then compare them.

```python
hand1 = HandParser([
    (Rank.KING, Suit.SPADE),
    (Rank.ACE, Suit.SPADE)
])

hand2 = HandParser([
    (Rank.NINE, Suit.SPADE),
    (Rank.TWO, Suit.CLUB)
])

board = [
    (Rank.EIGHT, Suit.SPADE),
    (Rank.TEN, Suit.SPADE),
    (Rank.JACK, Suit.SPADE),
    (Rank.QUEEN, Suit.SPADE),
    (Rank.TWO, Suit.HEART)
]

# This is the same as adding the cards 
# in the HandParser constructor
hand1 += board # add the board to hand1
hand2 += board # add the board to hand2

hand1.parse()
hand2.parse()

print(hand1.handenum) # Hand.STRAIGHTFLUSH
print(hand2.handenum) # Hand.STRAIGHTFLUSH
print(hand1 > hand2) # True
```

It is also possible to fetch hand's kickers.

```python
hand = HandParser([
    (Rank.TWO, Suit.DIAMOND),
    (Rank.ACE, Suit.CLUB),
    (Rank.TWO, Suit.SPADE),
    (Rank.THREE, Suit.DIAMOND),
    (Rank.TEN, Suit.HEART),
    (Rank.SIX, Suit.HEART),
    (Rank.KING, Suit.CLUB)
])

hand.parse()
print(list(hand.kickercards))
# [
#   (<Rank.ACE: 12>, <Suit.CLUB: 1>),
#   (<Rank.KING: 11>, <Suit.CLUB: 1>),
#   (<Rank.TEN: 8>, <Suit.HEART: 3>)
# ]
```

Note that `kickers` attribute saves the indices of `hand.cards` that form `kickercards`.

Using HandParser, we can estimate the probability of a given hand winning the game with given known cards on the table (as implemented in another python cli-app [here](https://github.com/cookpete/poker-odds)). We do this by repeatedly random-sampling hands, then averaging the wins. Mathematically, this process converges to the probability by the law of large numbers.

```python
from random import sample
from itertools import product
from pokerlib import HandParser
from pokerlib.enums import Rank, Suit

def getWinningProbabilities(players_cards, board=[], n=1000):
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
        for hand in hands: hand.parse()
        winner = max(hands)
        for i, hand in enumerate(hands):
            if hand == winner: wins[i] += 1

    return [win / n for win in wins]
    
w1, w2 = getWinningProbabilities([
    [(Rank.ACE, Suit.HEART), (Rank.KING, Suit.HEART)],
    [(Rank.KING, Suit.SPADE), (Rank.KING, Suit.DIAMOND)]
])
```

### Poker Game
A poker table can be established by providing its configuration.
A poker table object responds to given input with appropriate output,
which can be customized by overriding the two functions producing it.

```python
from pokerlib import Player, PlayerGroup, Table

# just print the output
class MyTable(Table):
    def publicOut(self, out_id, **kwargs):
        print(out_id, kwargs)
    def privateOut(self, player_id, out_id, **kwargs):
        print(out_id, kwargs)

table = MyTable(
    table_id = 0
    seats = 2
    players = PlayerGroup([])
    buyin = 100
    small_blind = 5
    big_blind = 10
)
```

Players could be passed inside MyTable constructor, 
but as they usually join the table after its definition, 
we will do that below.

```python
player1 = Player(
    table_id = table.id,
    _id = 1,
    name = 'alice',
    money = table.buyin
)
player2 = Player(
    table_id = table.id,
    _id = 2,
    name = 'bob',
    money = table.buyin
)
table += [player1, player2]
```

Communication with the `table` object is established through specified enums,
which can be modified by overriding table's `publicIn` method. 
Using enums, we can implement a poker game as shown below.

```python
from pokerlib.enums import RoundPublicInId, TablePublicInId

table.publicIn(player1.id, TablePublicInId.STARTROUND)
table.publicIn(player1.id, RoundPublicInId.CALL)
table.publicIn(player2.id, RoundPublicInId.CHECK)
table.publicIn(player1.id, RoundPublicInId.CHECK)
table.publicIn(player2.id, RoundPublicInId.RAISE, raise_by=50)
table.publicIn(player1.id, RoundPublicInId.CALL)
table.publicIn(player1.id, RoundPublicInId.CHECK)
table.publicIn(player2.id, RoundPublicInId.CHECK)
table.publicIn(player1.id, RoundPublicInId.ALLIN)
table.publicIn(player2.id, RoundPublicInId.CALL)
```

Wrong inputs are mostly ignored, though they can produce a response, 
when that seems useful. As noted before, when providing input,
the `table` object responds with output ids (e.g. `PLAYERACTIONREQUIRED`)
along with additional data that depends on the output id.
For all possible outputs, check `RoundPublicInId` and `TablePublicInId` enums.

A new round has to be initiated by one of the players every time the previous one ends (or at the beginning). A simple command line game, where you respond by enum names, can be implemented as below (for working version check `tests/round_test.py`).

```python
# define a table with fixed players as before
table = ...
while table:
    while table and not table.round:
        table.publicIn(
            table.players[0].id, 
            TablePublicInId.STARTROUND
        )

    player = table.round.current_player
    inp = input(f"require input from {player.id}: ")

    if inp in RoundPublicInId.__members__:
        action, raise_by = RoundPublicInId.__members__[inp], 0
    elif inp.startswith(RoundPublicInId.RAISE.name):
        raise_by = int(inp.split()[1])
        action, raise_by = RoundPublicInId.RAISE, raise_by
    else:
        continue

    table.publicIn(player.id, action, raise_by=raise_by)
```

## Tests
Basic tests for this library are included. You can test handparser by running
```bash
python tests/handparser.py
```
and the poker game by calling
```bash
python tests/round_test.py <player_number>
```
which will run a poker game simulation with raw data getting printed to stdout.

## License
GNU General Public License v3.0

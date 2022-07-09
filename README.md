# pokerlib

[![PyPI version](https://badge.fury.io/py/pokerlib.svg)](https://pypi.org/project/pokerlib)

## General

A Python poker library which focuses on simplifying a poker game implementation,
when its io is supplied. It includes modules that help with hand parsing and poker game continuation.

One application of this library was made by the PokerMessenger app,
which supplies library with io in the form of messenger group threads.
The app's repo is at https://github.com/kuco23/pokermessenger.

## Usage

Library consists of a module for parsing cards, which can be used seperately, and modules for running a poker game.

### HandParser

This module allows for parsing of hands. A hand usually consists of 2 dealt cards plus 5 on the board, but you can use this
for any number of cards.

```python
from pokerlib import HandParser
from pokerlib.enums import Rank, Suit, Hand

hand = [
    (Rank.SEVEN, Suit.HEART),
    (Rank.EIGHT, Suit.SPADE),
    (Rank.KING, Suit.DIAMOND),
    (Rank.ACE, Suit.DIAMOND),
    (Rank.QUEEN, Suit.DIAMOND),
    (Rank.JACK, Suit.DIAMOND),
    (Rank.TEN, Suit.DIAMOND)
]

parser = HandParser(hand)
parser.parse()
print(parser.handenum) # <Hand.STRAIGHTFLUSH: 8>
```

All of the enums used are of type `IntEnum`, so you can also specify cards as integers (look at `pokerlib.enums` file to see the exact enumeration of ranks and suits). You can also compare different hands as

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

hand1 += board
hand2 += board

hand1.parse()
hand2.parse()

print(hand1.handenum) # Hand.STRAIGHTFLUSH
print(hand2.handenum) # Hand.STRAIGHTFLUSH
print(hand1 > hand2) # True
```

you can also get kickers for a hand,

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
print(hand.kickercards)
# [
#   (<Rank.ACE: 12>, <Suit.CLUB: 1>),
#   (<Rank.KING: 11>, <Suit.CLUB: 1>),
#   (<Rank.TEN: 8>, <Suit.HEART: 3>)
# ]
```

FWY `kickers` attribute saves the indices of `hand.cards` that form the `kickercards`.

### Poker Game

We can establish a poker table by defining its configuration. Table also generates
output and we need to provide a function that handles it

```python
from pokerlib import Player, PlayerGroup, Table

# just print output
class MyTable(Table):
    def publicOut(self, action, **kwargs):
        print(action, kwargs)

table_id = 0
seats = 2
players = PlayerGroup([])
buyin = 100
small_blind = 5
big_blind = 10

table = MyTable(
    table_id, seats, players,
    buyin, small_blind, big_blind
)
```

To add players, we can do

```python
userid1 = 1
userid2 = 2
username1 = 'foo'
username2 = 'bar'

player1 = Player(table_id, userid1, username1, 100)
player2 = Player(table_id, userid2, username2, 100)

table += [player1, player2]
```

where 100 is the buyin amount. From here on, communication to the `table` object is established through enums:

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

Wrong inputs are mostly ignored, and additional outputs are generated to
keep players informed of the game continuation (like e.g. `PLAYERACTIONREQUIRED`).
For all possible outputs check `RoundPublicInId` and `TablePublicInId` enums.
A new round has to be initiated by one of the players every time it ends.

## Tests

Basic tests for this library are included.
For instance `round_test.py` can be started from os terminal, by typing `python round_test.py <player_num> <game_type>`, after which a simulation is run with not-that-informative data getting printed in stdout.

## License

GNU General Public License v3.0

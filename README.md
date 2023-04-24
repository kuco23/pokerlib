# pokerlib
[![PyPI version](https://badge.fury.io/py/pokerlib.svg)](https://pypi.org/project/pokerlib)

A lightweight Python poker library, focusing on simplifying a Texas hold'em poker game implementation, when its io is supplied. It includes modules that help with hand parsing and poker game continuation.

To install, run
```bash
pip install pokerlib
```

## Usage
Library consists of a module for parsing cards, which can be used separately, and modules that aid in running a poker game.

### HandParser
This module takes care of hand parsing. A hand usually consists of 2 dealt cards plus 5 on the board, and `HandParser` is heavily optimized to work with up to 7 cards (with more than 7 cards, this is no longer Texas hold'em). A card is defined as a pair of two enums - Rank and Suit. All of the enums used are of `IntEnum` type, so you can also freely interchange them for integers. Below is an example of how to construct two different hands and then compare them.

```python
from pokerlib import HandParser
from pokerib.enums import Rank, Suit

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

# add new cards to each hand
hand1 += board # add the board to hand1
hand2 += board # add the board to hand2

print(hand1.handenum) # Hand.STRAIGHTFLUSH
print(hand2.handenum) # Hand.STRAIGHTFLUSH
print(hand1 > hand2) # True
```

> **note:**
> In the previous version, each hand had to be parsed manually with `hand.parse()`, now calling any of the methods requiring the hand to be parsed, triggers parsing automatically. This only happens once, except if the cards in a given hand change. The only way cards in a hand should change is through the `__iadd__` method. If this method is called with hand already parsed, the hand is considered unparsed.

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

print(list(hand.kickercards))
# [
#   (<Rank.ACE: 12>, <Suit.CLUB: 1>),
#   (<Rank.KING: 11>, <Suit.CLUB: 1>),
#   (<Rank.TEN: 8>, <Suit.HEART: 3>)
# ]
```
Using HandParser, we can [estimate the probability](https://github.com/kuco23/pokerlib/blob/master/examples/winning_probability.py) of a given hand winning the game with given known cards on the table (as implemented in another python cli-app [here](https://github.com/cookpete/poker-odds)). We do this by repeatedly random-sampling hands, then averaging the wins. Mathematically, this process converges to the probability by the law of large numbers.


### Poker Game
A poker table can be established by providing its configuration.
A poker table object responds to given input with appropriate output,
which can be customized by overriding the two functions producing it.

```python
from pokerlib import Table, Player, PlayerSeats

# table that prints outputs
class MyTable(Table):
    def publicOut(self, out_id, **kwargs):
        print(out_id, kwargs)
    def privateOut(self, player_id, out_id, **kwargs):
        print(out_id, kwargs)

# define a new table
table = MyTable(
    table_id = 0
    seats = PlayerSeats([None] * 9)
    buyin = 100
    small_blind = 5
    big_blind = 10
)
```

We could have seated players on the `seats` inside `MyTable` constructor,
but let's add them to the defined table.

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
# seat player1 at the first seat
table += player1, 0
# seat player2 at the first free seat
table += player2
```

Communication with the `table` object is established through specified enums,
which can be modified by overriding table's `publicIn` method.
Using enum IO identifiers, we can implement a poker game as shown below.

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

Wrong inputs are mostly ignored, though they can produce a response, when it seems useful. As noted before, when providing input, the `table` object responds with output ids (e.g. `PLAYERACTIONREQUIRED`) along with additional data that depends on the output id. For all possible outputs, check `RoundPublicInId` and `TablePublicInId` enums.

A new round has to be initiated by one of the players every time the previous one ends (or at the beginning). A simple command line game, where you respond by enum names, can be implemented simply as in `examples/round_simulate.py`.

The library is highly customizable, allowing you to override specific class methods such as `_showdown` that let you define the way that cards get shown (see `pokerlib/implementations/_no_muck_showdown_table.py`). The IO identifiers can also be extended or reduced and set either as `Table` or `Round` class attributes.

## Tests
Basic tests for this library are included. You can test HandParser by running
```bash
python tests/handparser_reactive.py
```
initiate a poker round simulation with
```bash
python tests/round_test.py <number_of_players>
```
which will run a poker game simulation with raw data getting printed to stdout. The HandParser functionality was also tested against another poker library [pokerface](https://github.com/AussieSeaweed/pokerface). You can run those tests with
```bash
python tests/handparser_against_pokerface.py
```

## License
GNU General Public License v3.0

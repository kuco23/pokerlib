# PokerLogic

## Intro
This is meant to be a project, focusing on a library, 
which would simplify poker game implementations.

Includes a library with classes that help with hand parsing, poker round and game continuation.
The library's main function is for its main class Round to be baseclassed and its IO methods overriden.

## Library applications

### PokerMessenger
One application of the library included is made with pokermessenger app where IO depends on the fbchat module. You can check out the app's repository [here]
(https://kuco23.github.io/pokermessenger/documentation.html).


## Code Example
This is an abstract example, showing how the library is supposed to be used.
```python
from pokerlib.enums import PlayerAction, PrivateOutId, PublicOutId
from pokerlib import HandParser
from pokerlib import Player, PlayerGroup
from pokerlib import Table, Round

class RoundSubclass(Round):
   
   def privateIn(self, raw_str, *args, **kwargs):
      # parse raw_str into arguments for processAction method
      self.processAction(PlayerAction.<action>)
     
   def privateOut(self, _id, *args, **kwargs):
      # define the method for outputing private information
      # (eg. player's cards), 
      # types of which are defined in PrivateOutId enum,
      # which is passed as _id
   
   def publicOut(self, _id, *args, **kwargs):
      # define the method for outputing public information
      # (eg. winner declaration),
      # types of which are defined in PublicOutId enum,
      # which is passed as _id

# define which round type should be used on the (poker) table
Table.Round = RoundSubclass

TABLE_ID = 0

PLAYER_BUYIN = <unsigned int>
SMALL_BLIND = <unsigned int>
BIG_BLIND = <unsigned int>

player_group = PlayerGroup(map(
    lambda pl, pi: Player(TABLE_ID, pl, pi, PLAYER_BUYIN),
    ['Player1', 'Player2', ... , 'PlayerN'],
    ['PlayerId1', 'PlayerId2', ... 'PlayerIdN']
))

table = Table(TABLE_ID, player_group, SMALL_BLIND, BIG_BLIND)

while True:
    while table and not table.round:
	table.newRound(0)
    if not table: break
    a = input(f"{table.round.current_player.id}: ")
    table.round.privateIn(a)
```


## Tests
Tests are included for the handparser and round files.
Test for round is started from the terminal and
requires one positional argument, 
which takes in the number of players and then runs the simulation.
For more information about the arguments run `python round_test.py --help`
from the os terminal.

## License
GNU General Public License v3.0

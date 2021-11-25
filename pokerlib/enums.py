from enum import IntEnum

class Rank(IntEnum):
    TWO = 0
    THREE = 1
    FOUR = 2
    FIVE = 3
    SIX = 4
    SEVEN = 5
    EIGHT = 6
    NINE = 7
    TEN = 8
    JACK = 9
    QUEEN = 10
    KING = 11
    ACE = 12

class Suit(IntEnum):
    SPADE = 0
    CLUB = 1
    DIAMOND = 2
    HEART = 3

class Hand(IntEnum):
    HIGHCARD = 0
    ONEPAIR = 1
    TWOPAIR = 2
    THREEOFAKIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULLHOUSE = 6
    FOUROFAKIND = 7
    STRAIGHTFLUSH = 8
    

class Turn(IntEnum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3

class RoundPublicInId(IntEnum):
    FOLD = 0
    CHECK = 1
    CALL = 2
    RAISE = 3
    ALLIN = 4

# codes sent from round to player
class RoundPrivateOutId(IntEnum):
    DEALTCARDS = 0

# codes sent from round to players
class RoundPublicOutId(IntEnum):
    NEWROUND = 1
    NEWTURN = 2
    SMALLBLIND = 4
    BIGBLIND = 5
    PLAYERCHECK = 6
    PLAYERCALL = 7
    PLAYERFOLD = 8
    PLAYERRAISE = 9
    PLAYERALLIN = 10
    PLAYERACTIONREQUIRED = 11
    PUBLICCARDSHOW = 12
    DECLAREPREMATUREWINNER = 13
    DECLAREFINISHEDWINNER = 14
    ROUNDFINISHED = 15

class TablePublicInId(IntEnum):
    STARTROUND = 0

class TablePublicOutId(IntEnum):
    PLAYERJOINED = 0
    PLAYERREMOVED = 1
    NEWROUNDSTARTED = 2
    ROUNDNOTINITIALIZED = 3
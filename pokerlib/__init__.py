"""pokerlib python library"""

from . import enums
from ._handparser import HandParser, HandParserGroup
from ._player import Player, PlayerGroup, PlayerSeats
from ._round import Round
from ._table import Table

__title__ = 'pokerlib'
__version__ = '2.1.1'
__description = 'Python poker library'

__author__ = 'Nejc Ševerkar'
__email__ = 'nseverkar@gmail.com'

__all__ = [
    'HandParser',
    'HandParserGroup',
    'Player',
    'PlayerGroup',
    'Round',
    'Table',
    'PlayerSeats'
]

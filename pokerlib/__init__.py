"""pokerlib python library"""

from . import enums
from ._handparser import HandParser, HandParserGroup
from ._player import Player, PlayerGroup
from ._round import Round
from ._table import Table

__title__ = 'pokerlib'
__version__ = '0.9.3'
__description = 'Python poker library'

__author__ = 'Nejc Ševerkar'
__email__ = 'nseverkar@gmail.com'

__all__ = [
    'HandParser',
    'HandParserGroup',
    'Player',
    'PlayerGroup',
    'Round',
    'Table'
]

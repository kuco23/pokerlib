"""pokerlib python library"""

from . import enums
from ._handparser import HandParser, HandParserGroup
from ._player import Player, PlayerGroup
from ._round import Round
from ._table import Table

__title__ = 'pokerlib'
__version__ = '1.0'
__description = 'python poker library'

__author__ = 'Nejc Ševerkar'
__email__ = 'nseverkar@gmail.com'

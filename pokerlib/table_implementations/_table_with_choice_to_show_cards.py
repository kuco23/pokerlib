from itertools import chain
from enum import IntEnum

from ..enums import RoundPublicOutId, RoundPublicInId
from .._round import Round
from .._table import Table

def extendedEnum(original, extended):
    return IntEnum(extended.__name__, [
        (x.name, x.value) for x in chain(original, extended)])

# extending RoundPublicInId enum by
class RoundWithChoiceToShowCardsPublicInId(IntEnum):
    SHOWCARDS = 5
RoundWithChoiceToShowCardsPublicInId = extendedEnum(
    RoundPublicInId, RoundWithChoiceToShowCardsPublicInId)

# extending RoundPublicOutId enum by
class RoundWithChoiceToShowCardsPublicOutId(IntEnum):
    PLAYERCHOICEREQUIRED = 14
    PLAYERREVEALCARDS = 15
RoundWithChoiceToShowCardsPublicOutId = extendedEnum(
    RoundPublicOutId, RoundWithChoiceToShowCardsPublicOutId)

class RoundWithChoiceToShowCards(Round):
    PublicInId = RoundWithChoiceToShowCardsPublicInId
    PublicOutId = RoundWithChoiceToShowCardsPublicOutId

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._premature_winner_id = None

    def _close(self):
        # ignore previous internal calls
        if self._premature_winner_id is None:
            super()._close()

    def _dealPrematureWinnings(self):
        super()._dealPrematureWinnings()
        winner, = self.players.getNotFoldedPlayers()
        self._premature_winner_id = winner.id
        self.publicOut(
            self.PublicOutId.PLAYERCHOICEREQUIRED,
            player_id = winner.id
        )

    def _showPrematureWinnerCards(self):
        winner = self.players.getPlayerById(self._premature_winner_id)
        self.publicOut(
            self.PublicOutId.PLAYERREVEALCARDS,
            player_id = winner.id,
            cards = winner.cards
        )

    def publicIn(self, player_id, action, raise_by=0, show_cards=False):
        # process all the standard inputs
        super().publicIn(player_id, action, raise_by)
        # add card reveal options (note that caller does not have to be current winner)
        if (
            action is self.PublicInId.SHOWCARDS and
            self._premature_winner_id is not None and self._premature_winner_id == player_id
        ):
            if show_cards: self._showPrematureWinnerCards()
            self._premature_winner_id = None
            self._close()

class TableWithChoiceToShowCards(Table):
    RoundClass = RoundWithChoiceToShowCards
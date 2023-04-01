from itertools import chain
from enum import IntEnum

from ..enums import RoundPublicOutId, TablePublicOutId
from .._round import Round
from .._table import Table

def extendedEnum(original, extended):
    return IntEnum(extended.__name__, [
        (x.name, x.value) for x in chain(original, extended)])

# extending RoundPublicInId enum by
class RoundWithChoiceToShowCardsPublicInId(IntEnum):
    SHOWCARDS = 5
RoundWithChoiceToShowCardsPublicInId = extendedEnum(
    RoundPublicOutId, RoundWithChoiceToShowCardsPublicInId)

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

    def publicOut(self, out_id, **kwargs):
        # otherwise account for premature winner
        super().publicOut(out_id, **kwargs)
        if out_id is self.PublicOutId.DECLAREPREMATUREWINNER:
            self.finished = False
            self._premature_winner_id = kwargs['player_id']
            self.publicOut(
                self.PublicOutId.PLAYERCHOICEREQUIRED,
                player_id = kwargs['player_id']
            )

    def publicIn(self, player_id, action, raise_by=0, show_cards=False):
        # process all the standard inputs
        super().publicIn(player_id, action, raise_by)
        # add card reveal options (note that caller does not have to be current winner)
        if (
            action is self.PublicInId.SHOWCARDS and
            self._premature_winner_id is not None and self._premature_winner_id == player_id
        ):
            if show_cards:
                player = self.players.getPlayerById(player_id)
                self.publicOut(
                    self.PublicOutId.PLAYERREVEALCARDS,
                    player_id = player_id,
                    cards = player.cards
                )
            self._premature_winner_id = None
            self._close()

class TableWithChoiceToShowCards(Table):
    RoundClass = RoundWithChoiceToShowCards
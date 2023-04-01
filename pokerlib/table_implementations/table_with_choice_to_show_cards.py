from enum import IntEnum

from ..enums import RoundPublicOutId, TablePublicOutId
from .._round import Round
from .._table import Table


# extending RoundPublicInId enum by
class RoundWithChoiceToShowCardsPublicInId(IntEnum):
    SHOWCARDS = 5

# extending RoundPublicOutId enum by
class RoundWithChoiceToShowCardsPublicOutId(IntEnum):
    PLAYERCHOICEREQUIRED = 14
    PLAYERREVEALCARDS = 15

class RoundWithChoiceToShowCards(Round):

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
        if out_id is RoundPublicOutId.DECLAREPREMATUREWINNER:
            self.finished = False
            self._premature_winner_id = kwargs['player_id']
            self.publicOut(
                RoundWithChoiceToShowCardsPublicOutId.PLAYERCHOICEREQUIRED,
                player_id = kwargs['player_id']
            )

    def publicIn(self, player_id, action, raise_by=0, show_cards=False):
        # process all the standard inputs
        super().publicIn(player_id, action, raise_by)
        # add card reveal options (note that caller does not have to be current winner)
        if (
            action is RoundWithChoiceToShowCardsPublicInId.SHOWCARDS and
            self._premature_winner_id is not None and self._premature_winner_id == player_id
        ):
            if show_cards:
                player = self.players.getPlayerById(player_id)
                self.publicOut(
                    RoundWithChoiceToShowCardsPublicOutId.PLAYERREVEALCARDS,
                    player_id = player_id,
                    cards = player.cards
                )
            self._premature_winner_id = None
            self._close()

class TableWithChoiceToShowCards(Table):
    RoundClass = RoundWithChoiceToShowCards

    def publicIn(self, player_id, action, **kwargs):
        # extend table input actions
        if action in RoundWithChoiceToShowCardsPublicInId:
            if not self.round: self.publicOut(
                TablePublicOutId.ROUNDNOTINITIALIZED)
            else: self.round.publicIn(player_id, action)
        else:
            super().publicIn(player_id, action, **kwargs)
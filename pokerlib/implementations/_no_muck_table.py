from .._round import Round
from .._table import Table


class NoMuckRound(Round):
    def publicOut(self, out_id, **kwargs):
        if out_id is self.PublicOutId.PLAYERCHOICEREQUIRED:
            return self.publicIn(kwargs['player_id'], self.PublicInId.SHOW)
        super().publicOut(out_id, **kwargs)

class NoMuckTable(Table):
    RoundClass = NoMuckRound
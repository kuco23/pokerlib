from .._round import Round
from .._table import Table

class NoMuckShowdownRound(Round):
    def _showdown(self):
        for player in self.players:
            if not player.is_folded: self.publicOut(
                self.PublicOutId.PUBLICCARDSHOW,
                player_id = player.id,
                cards = player.cards,
                kickers = player.group_kickers
            )

class NoMuckShowdownTable(Table):
    RoundClass = NoMuckShowdownRound
class PlayerCannotJoinTable(Exception):
    def __init__(self, player_id, table_id, reason):
        super().__init__(
            f'Player {player_id} cannot join table {table_id} '
            f'because of {reason}'
        )

class TableError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
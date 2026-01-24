# commands/military.py
from .base import register_command

@register_command("move_fleet")
class MoveFleet:
    def __init__(self, fleet_id, x, y):
        self.fleet_id = fleet_id
        self.target = (x, y)

    def execute(self, game_state):
        # Logic goes here
        pass
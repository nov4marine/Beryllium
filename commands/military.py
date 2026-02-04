# commands/military.py
from .base import register_command, Command

@register_command("move_fleet")
class MoveFleet(Command):
    def __init__(self, fleet_id, x, y):
        self.fleet_id = fleet_id
        self.target = (x, y)

    def execute(self, game_state):
        # Logic goes here
        pass
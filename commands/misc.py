# commands/misc.py
from .base import register_command

@register_command("switch_view")
class SwitchViewCommand:
    def __init__(self, target_system_id):
        self.target_system_id = target_system_id

    def execute(self, player_id, game_state):
        # Update the server's record of what this player is watching
        session = game_state.get_session(player_id)
        session.current_view = self.target_system_id
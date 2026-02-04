# commands/misc.py
from .base import register_command, Command

@register_command("switch_view")
class SwitchViewCommand(Command):
    def __init__(self, new_view, solar_system=None):
        self.current_view = new_view
        self.current_solar_system = solar_system # ID of the solar system

    def execute(self, game_model, client_session):
        # Update the server's record of what this player is watching
        client_session.current_view = self.current_view
        client_session.current_solar_system = self.current_solar_system

@register_command("galaxy_setup_data")
class GalaxySetupDataCommand(Command):
    def execute(self, game_model, client_session):
        client_session.append_response({
            "galaxy_setup": game_model.galaxy.setup_dict()
        })


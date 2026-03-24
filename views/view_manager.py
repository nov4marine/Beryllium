import arcade
from views.galaxy_view import GalaxyView
from views.solar_system_view import SolarSystemView
from views.persistent_ui import PersistentUI


class ViewManager:
    def __init__(self, window, game_model, asset_manager):
        self.window = window
        self.game_model = game_model
        self.asset_manager = asset_manager

        # Persistent UI (HUD elements)
        self.persistent_ui = PersistentUI(game_model, asset_manager)
        self.window.persistent_ui = self.persistent_ui

        # Initialize views
        self.views = {
            "galaxy": GalaxyView(game_model),
            # Add other views here as needed
            "solar_system": SolarSystemView(game_model),
            # "planet_menu": PlanetMenu(game_model),
        }

        # Set the initial view
        self.current_view = None
        self.show_view("galaxy")

    def show_view(self, view_name):
        """Switch to the specified view."""
        if view_name in self.views:
            self.current_view = self.views[view_name]
            self.window.show_view(self.current_view)
        else:
            raise ValueError(f"View '{view_name}' does not exist.")

    def update_persistent_ui(self, player_nation):
        """Update the persistent UI with the current player nation."""
        self.persistent_ui.set_player_nation(player_nation)

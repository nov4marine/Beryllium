import arcade
import arcade.gui
from model.model import GameModel
from model.world.calendar import Calendar
from views.galaxy_view import GalaxyView
# from views.solar_system_view import SolarSystemView
from views.ui_stuff import PersistentUI
from model.assets import AssetManager


class MyGame:
    def __init__(self):
        self.game_model = GameModel()  # Central simulation

        self.width = 1920
        self.height = 1080
        self.title = "Beryllium"
        self.window = arcade.Window(
            width=self.width,
            height=self.height,
            title=self.title
        )

        # Window Components
        self.window.calendar = Calendar()
        self.window.asset_manager = AssetManager()
        self.window.persistent_ui = PersistentUI(self.game_model, self.game_model.player_nation)

        # --- Resources to load ---
        self.game_model.initialize_new_game()
        self.galaxy_view = GalaxyView(game_model=self.game_model)
        self.main_menu_view = None

        self.window.show_view(self.galaxy_view)


if __name__ == "__main__":
    game = MyGame()
    arcade.run()

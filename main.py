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

        calendar = self.game_model.calendar

        self.width = 1920
        self.height = 1080
        self.title = "Beryllium"
        self.window = arcade.Window(
            width=self.width,
            height=self.height,
            title=self.title,
        )

        print(f"Default texture atlas size: {self.window.ctx.default_atlas.width}x{self.window.ctx.default_atlas.height}")
        self.window.ctx.default_atlas.resize((8192, 8192))

        # Window Components
        self.window.calendar = calendar
        self.window.asset_manager = AssetManager()
        self.window.persistent_ui = PersistentUI(self.game_model, self.window.asset_manager)

        calendar.add_daily_observer(self.window.persistent_ui)
        calendar.add_monthly_observer(self.window.persistent_ui)

        # --- Resources to load ---
        self.game_model.initialize_new_game()
        self.window.persistent_ui.player_nation = self.game_model.player_nation
        self.galaxy_view = GalaxyView(game_model=self.game_model)
        self.main_menu_view = None
        
        self.window.show_view(self.galaxy_view)


if __name__ == "__main__":
    game = MyGame()
    arcade.run()

"""
TODO: 
1. Go over economy loop from the top down. make sure everything is working as intended.
2. Get building GUI to a workable state, even if that means backing down to text labels. 
3. Refactor game setup to a collected, organized form.
4. Refactor game setup to start "in motion" instead of 100% unemployment and no statistics. 
5. Incrementally expand planet menu to a functional state, again being tolerant of text in place of graphs.
6. Investment system is currently a template and must transition to a workable state. 
7. CREATE A DOCUMENT FOR PLANS. Too many features are falling apart in the details because I don't remember them. 
8. CREATE A MAP of systems on the code side of things. Need a visual for how various systems interact. 
9. Learn how to do logging. Embrace excitement of true spreadsheet simulation.
10. Pytest? Kind of 9 and a half here ^
"""
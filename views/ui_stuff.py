import arcade
import arcade.gui
from views.UI_stuff.planet_menu import PlanetMenu


class PersistentUI:
    """Baiscally the primary GUI that is always on screen, or has elements that persist across views"""
    def __init__(self, game_model, asset_manager):
        self.game_model = game_model
        self.asset_manager = asset_manager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.player_nation = None

        # --- Sub-Components ---
        self.planet_menu = PlanetMenu(game_model, self.asset_manager)

        # --- HUD ---
        self.root = self.manager.add(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.resource_bar = arcade.gui.UIAnchorLayout(size_hint=(1, 0.05))
        self.resource_bar.with_background(color=arcade.color.DARK_IMPERIAL_BLUE)
        self.root.add(self.resource_bar, anchor_y="top")

        # --- Create the top resource bar ---
        self.flag = arcade.gui.UISpace(color=arcade.color.RED, size_hint=(0.05, 1))

        self.resource_bar.add(self.flag, anchor_x="left")
        # --- Stats ---
        self.stats = arcade.gui.UIBoxLayout(vertical=False, size_hint=(0.95, 1))
        self.gdp = arcade.gui.UILabel(text="GDP")
        self.gdp_per_capita = arcade.gui.UILabel(text="GDP per capita")
        self.population = arcade.gui.UILabel(text="Population")

        self.stats.add(self.gdp)
        self.stats.add(self.gdp_per_capita)
        self.stats.add(self.population)

        self.resource_bar.add(self.stats, anchor_x="right")
        # education
        self.standard_of_living = arcade.gui.UILabel(text="Standard of Living")
        self.radicals = arcade.gui.UILabel(text="Radicals")
        self.loyalists = arcade.gui.UILabel(text="Loyalists")
        # --- Resources ---
        self.bureaucracy = arcade.gui.UILabel(text="Bureaucracy")
        self.authority = arcade.gui.UILabel(text="Authority")
        self.treasury = arcade.gui.UILabel(text="Treasury")
        # --- Other Stats ---
        self.tech = arcade.gui.UILabel(text="Technology")
        self.starbases = arcade.gui.UILabel(text="Starbases")
        # military
        # --- Time ---
        self.calendar = arcade.gui.UIAnchorLayout(size_hint=(0.1, 1))
        # self.calendar = arcade.gui.UISpriteWidget()
        self.calendar.with_background(color=arcade.color.ARMY_GREEN)
        self.date = arcade.gui.UILabel(text=self.game_model.calendar.__str__())
        self.calendar.add(self.date)
        self.resource_bar.add(self.calendar, anchor_x="right")

    def draw(self):
        self.manager.draw()
        self.planet_menu.draw()

    def on_monthly_update(self):
        self.gdp.text = self.player_nation.gdp
        self.gdp_per_capita.text = self.player_nation.gdp_per_capita
        self.population.text = self.player_nation.population

        self.standard_of_living.text = self.player_nation.standard_of_living
        self.loyalists.text = self.player_nation.loyalists
        self.radicals.text = self.player_nation.radicals

        self.bureaucracy.text = self.player_nation.bureaucracy
        self.authority.text = self.player_nation.authority
        self.treasury.text = self.player_nation.treasury

    def on_daily_update(self):
        self.date.text = self.game_model.calendar.__str__()

    def show_planet_menu(self, colony):
        self.planet_menu.open_window(colony)

class GalaxyStarLabel:
    def __init__(self, body):
        self.body = body
        self.text = arcade.Text(
            text=body.name,
            x=body.x,
            y=body.y - 40,
            color=(180, 180, 180, 180),
            font_size=24,
            anchor_x="center"
        )

    def draw(self):
        self.text.draw()

class PlanetLabel:
    def __init__(self, body):
        self.body = body
        position = body.get_position()
        self.text = arcade.Text(
            text=body.name,
            x=position[0],
            y=position[1] - 40,
            color=(180, 180, 180, 180),
            font_size=24,
            anchor_x="center"
        )
        
    def draw(self):
        self.text.draw()
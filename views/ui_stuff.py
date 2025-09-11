import arcade
import arcade.gui
from views.UI_stuff.planet_menu import PlanetInterface


class PersistentUI:
    def __init__(self, game_model, player_nation):
        self.game_model = game_model
        self.manager = arcade.gui.UIManager()
        self.player_nation = player_nation

        # --- Sub-Components ---
        planet_interface = PlanetInterface(game_model, player_nation)

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
        self.calendar = arcade.gui.UILabel(text="Date")
        # self.calendar = arcade.gui.UISpriteWidget()

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

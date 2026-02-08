import arcade
import arcade.gui
from arcade.gui import UIAnchorLayout, UILabel, UIFlatButton

class LeftSideBar:
    def __init__(self, persistent_ui, manager, asset_manager):
        self.persistent_ui = persistent_ui
        self.manager = manager
        self.assets = asset_manager
        self.collapsed = True
        self.root = self.manager.add(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.collapsed_panel = arcade.gui.UIBoxLayout(size_hint=(0.04, 0.5))
        self.collapsed_panel.with_background(color=arcade.color.DARK_BLUE_GRAY)
        # add widgets to collapsed panel
        self.collapsed_button = arcade.gui.UIFlatButton(size_hint=(1, 1))

        @self.collapsed_button.event("on_click")
        def on_click_collapsed_button(event):
            self.persistent_ui.show_market_gui()

        self.collapsed_panel.add(self.collapsed_button)
        self.root.add(self.collapsed_panel, anchor_x="left", anchor_y="center")


class RightLedger:
    def __init__(self, persistentui, manager, asset_manager):
        self.persistentui = persistentui
        self.manager = manager
        self.assets = asset_manager
        self.root = self.manager.add(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.ledger_panel = arcade.gui.UIBoxLayout(size_hint=(0.1, 0.7), space_between=5)
        self.ledger_panel.with_background(color=arcade.color.DARK_GRAY)
        self.root.add(self.ledger_panel, anchor_x="right", anchor_y="center")
        # add widgets to ledger panel
        self.ledger_title = arcade.gui.UILabel(text="Ledger", size_hint=(1, 0.01), align="center")
        self.ledger_title.with_background(color=arcade.color.DARK_IMPERIAL_BLUE)
        self.ledger_title.with_border()
        self.ledger_panel.add(self.ledger_title)

        self.planets = arcade.gui.UIBoxLayout(space_between=5)
        self.ledger_panel.add(self.planets)

    def update(self, nation):
        self.planets.clear()
        for colony in nation.colonies:
            print(colony.name)
            planet_button = arcade.gui.UIFlatButton(text=colony.name, width=150, height=30)
            self.planets.add(planet_button)
            
        @planet_button.event("on_click")
        def on_click_planet_button(event):
            self.persistentui.show_planet_menu(colony)

class TopBar(UIAnchorLayout):
    def __init__(self, persistentui, asset_manager):
        self.persistentui = persistentui
        self.player_nation = None
        self.assets = asset_manager
        self.size_hint = (1, 0.05)
        self.with_background(color=arcade.color.DARK_IMPERIAL_BLUE)

        # ---From left to right: ---

        # Flag and added
        self.flag = arcade.gui.UISpace(color=arcade.color.RED, size_hint=(0.05, 1))
    #TODO: add a flag sprite that actually uses the player's nation. Serves as a quick visual indicator.
        self.add(self.flag, anchor_x="left")

        # Core Stats Box and added
        self.stats_box = arcade.gui.UIBoxLayout(vertical=False, size_hint=(0.95, 1), space_between=10)
        self.add(self.stats_box, anchor_x="right")

        # Treasury/Budget
        self.treasury = UILabel(text="Treasury: 0")
        self.budget = UILabel(text="Monthly Income: 0")
        
        # Add Treasury/Budget
        self.stats_box.add(self.treasury)
        self.stats_box.add(self.budget)

        # Economy
        self.gdp = UILabel(text="GDP: 0")
        self.gdp_per_capita = UILabel(text="GDP/Capita: 0")
        self.population = UILabel(text="Population: 0")

        # Add Economy
        self.stats_box.add(self.gdp)
        self.stats_box.add(self.gdp_per_capita)
        self.stats_box.add(self.population)

        # Space
        space1 = arcade.gui.UISpace(size_hint=(0.01, 1), color=arcade.color.LIGHT_SKY_BLUE)
        self.stats_box.add(space1)

        # Social
        self.standard_of_living = UILabel(text="Standard of Living: 0")
        self.radicals = UILabel(text="Radicals: 0")
        self.loyalists = UILabel(text="Loyalists: 0")

        # Add Social
        self.stats_box.add(self.standard_of_living)
        self.stats_box.add(self.radicals)
        self.stats_box.add(self.loyalists)

        # Later add tech, starbases, etc.

        # Calendar
        # self.calendar_box = SpriteWidget() # later add calendar art to this
        self.display = UIFlatButton(text="1.1.2200", size_hint=(0.1, 1), font_size=18, bg=arcade.color.EMERALD)
        
        @self.display.event("on_click")
        def on_click_calendar(event):
            self.persistentui.calendar.toggle_pause()  # Toggle pause to allow manual advancement of time without the calendar automatically advancing every second.

        # Add Calendar
        self.add(self.display, anchor_x="right")

    def on_daily_update(self):
        date = self.persistentui.calendar.current_date
        self.display.text = date
        if self.player_nation is not None:
            try:
                self.treasury.text = f"Treasury: {self.player_nation.treasury}"
                self.budget.text = f"Monthly Income: {self.player_nation.monthly_income}"
                self.gdp.text = f"GDP: {self.player_nation.gdp}"
                self.gdp_per_capita.text = f"GDP/Capita: {self.player_nation.gdp_per_capita}"
                self.population.text = f"Population: {self.player_nation.population}"
                self.standard_of_living.text = f"Standard of Living: {self.player_nation.standard_of_living}"
                self.radicals.text = f"Radicals: {self.player_nation.radicals}"
                self.loyalists.text = f"Loyalists: {self.player_nation.loyalists}"
                print(f"Updated TopBar stats for {self.player_nation.name}")
            except Exception as e:
                print(f"Error updating TopBar stats: {e}")

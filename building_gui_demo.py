import arcade
import arcade.gui

from model.assets import AssetManager
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_TITLE = "Starting Template"


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.AMAZON

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.root = arcade.gui.UIAnchorLayout()
        self.ui_manager.add(self.root)

        self.winddow = GenericMenu(title="Planet Info")
        self.root.add(self.winddow)
        # If you have sprite lists, you should create them here,
        # and set them to None

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()
        self.ui_manager.draw()  # Draw the UI manager (and all its components)

        # Call draw() on all your sprite lists below

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass


import arcade
from arcade.gui import UIAnchorLayout

class GenericMenu(UIAnchorLayout):
    def __init__(self, title="Menu Title", asset_manager=None):
        super().__init__(size_hint=(0.7, 0.7))
        self.with_background(color=arcade.color.DARK_SLATE_GRAY)

        self.asset_manager = asset_manager

        # Title bar
        self.top_bar = UIAnchorLayout(size_hint=(1, 0.08))
        self.top_bar.with_background(color=arcade.color.DARK_BLUE_GRAY)
        self.title_label = arcade.gui.UILabel(text=title, font_size=18)
        self.close_button = arcade.gui.UIFlatButton(text="X", size_hint=(0.08, 0.8))
        self.close_button.on_click = self.close_window

        self.top_bar.add(self.title_label, anchor_x="center")
        self.top_bar.add(self.close_button, anchor_x="right")
        self.add(self.top_bar, anchor_y="top")

        # Content area
        self.content_frame = UIAnchorLayout(size_hint=(1, 0.92))
        self.content_frame.with_background(color=arcade.color.CHARCOAL)
        self.add(self.content_frame, anchor_y="bottom")

    def close_window(self, event=None):
        print("Closing menu")
        self.visible = False  # Or remove from parent
        #self.parent.remove(self)  # If you want to remove it from the UI manager
        # Ideally probably have 1 of every menu and just show/hide and update content as needed, instead of creating/destroying them

    def open_window(self):
        self.visible = True


class PlanetMenu(GenericMenu):
    """
    A menu window for displaying and managing a planet/colony.
    Inherits from GenericMenu. Overrides setup_content() to create tabs and content areas.
    Call set_planet(colony) to set the current colony to display.
    All content must be added to the content_frame defined in GenericMenu. (and probably cleared first)
    """

    def __init__(self):
        super().__init__()
        self.planet = None  # This will hold the current colony/planet object whose info we want to display
        self.colony = self.planet.colony if self.planet and self.planet.colony else None
        self.current_tab = None
        # Utilities 
        # RGBA: (R, G, B, A), where A is 0 (fully transparent) to 255 (fully opaque)
        self.semi_transparent_bg = (30, 30, 30, 180)  # Dark gray, mostly opaque

        self.grid = arcade.gui.UIGridLayout(size_hint=(1, 1), row_count=3, column_count=4)
        self.grid.with_background(color=arcade.color.CHARCOAL)
        self.content_frame.add(self.grid)

        tabs = arcade.gui.UIButtonRow()
        tabs.add_button("Summary")
        tabs.add_button("Economy")

        @tabs.event("on_action")
        def on_click_tab(event):
            print("Tab clicked:", event.action)
            if event.action == "Summary":
                print("Switching to Summary tab")
                self.show_summary_tab()
            elif event.action == "Economy":
                print("Switching to Economy tab")
                self.show_economy_tab()
        self.content_frame.add(tabs, anchor_x="left", anchor_y="bottom", align_y=-50)

    def box1(self):
        # --- Box 1 --- Primary planet art and info with governor portrait and name
        box1 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Primary planet art and info
        #climate = self.planet.planet.climate if self.planet and self.planet.planet else "not_implemented"
        climate = self.planet.climate if self.planet else "continental"
        climate_background = self.asset_manager.ui_art.get(climate, self.asset_manager.ui_art["default"])
        box1.with_background(texture=climate_background)
        box1.with_border()

        stats_box = arcade.gui.UIBoxLayout(vertical=False, size_hint=(1, 0.1), space_between=50)  # Key stats
        stats_box.with_padding(all=10)
        stats_box.with_background(color=self.semi_transparent_bg)
        self.gdp_label = arcade.gui.UILabel(text=f"GDP: {self.colony.local_bls.statistics.get('gdp', 'N/A')}")
        self.population_label = arcade.gui.UILabel(
            text=f"Population: {self.colony.local_bls.statistics.get('population', 'N/A')}")
        self.stability_label = arcade.gui.UILabel(
            text=f"Stability: {self.colony.local_bls.statistics.get('stability', 'N/A')}")
        self.unemployment_label = arcade.gui.UILabel(
            text=f"Unemployment: {self.colony.local_bls.statistics.get('unemployment_rate', 'N/A')}%")

        stats_box.add(self.gdp_label)
        stats_box.add(self.population_label)
        stats_box.add(self.stability_label)
        stats_box.add(self.unemployment_label)
        box1.add(stats_box, anchor_y="bottom")
        self.grid.add(box1, row=0, column=0, column_span=3)


    def open_window(self, colony):
        self.colony = colony
        #self.refresh(colony)
        self.title_label.text = getattr(colony, 'name', f"{self.planet.name}")
        self.show_summary_tab()
        self.visible = True

    def show_summary_tab(self):
        self.grid.clear()  # Clear previous content
        self.current_tab = "Summary"

        # --- Box 1 --- Primary planet art and info with governor portrait and name
        self.box1()
        climate = self.planet.climate if self.planet else "continental"

        # --- Box 2 --- Buildings overview
        box2 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Buildings overview
        box2.with_border()
        self.grid.add(box2, row=1, column=0, column_span=2, row_span=2)

        urban_box = arcade.gui.UIAnchorLayout(size_hint=(1, 0.5))  # Urban buildings
        urban_box.with_border()
        urban_label = arcade.gui.UILabel(text="Urban Buildings")
        urban_buildings = arcade.gui.UIBoxLayout(vertical=False, size_hint=(1, 0.9), space_between=10)
        urban_buildings.with_padding(all=100)
        # --- Urban buildings grid ---
        urban_building_list = []
        if self.colony and self.colony.buildings:
            # only do the first 6 urban buildings for now 
            for building in self.colony.buildings:
                if building.geography == "Urban":
                    urban_building_list.append(building)
            for building in urban_building_list[:7]:
                urban_button = BuildingWidget(self, building, self.asset_manager, size=100)
                urban_buildings.add(urban_button)

        urban_box.add(urban_label, anchor_y="top")
        urban_box.add(urban_buildings, anchor_x="center", anchor_y="center")
        box2.add(urban_box, anchor_y="top")

        rural_box = arcade.gui.UIAnchorLayout(size_hint=(1, 0.5))  # Rural buildings
        rural_box.with_border()
        rural_label = arcade.gui.UILabel(text="Rural Buildings")
        rural_buildings = arcade.gui.UIBoxLayout(vertical=False, size_hint=(1, 0.9), space_between=10)
        rural_buildings.with_padding(all=100)
        # --- Rural buildings grid ---
        rural_buildings_list = []
        if self.colony and self.colony.buildings:
            for building in self.colony.buildings:
                if building.geography == "Rural":
                    rural_buildings_list.append(building)
            for building in rural_buildings_list[:7]:
                rural_widget_button = BuildingWidget(self, building, self.asset_manager, size=100)
                rural_buildings.add(rural_widget_button)

        rural_box.add(rural_label, anchor_y="top")
        rural_box.add(rural_buildings, anchor_y="center", anchor_x="center")
        box2.add(rural_box, anchor_y="bottom")

        # --- Box 3 --- Celestial body info
        box3 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # celestial body info
        box3.with_border()
        box3.with_background(
            texture=self.asset_manager.ui_art.get("solar_system_background", self.asset_manager.ui_art["default"]))
        self.grid.add(box3, row=0, column=3)

        planet_info = arcade.gui.UIBoxLayout(vertical=True, size_hint=(0.5, 1), space_between=10, anchor_y="center")
        planet_label = arcade.gui.UILabel(text="Planet Summary", bold=True)
        climate_label = arcade.gui.UILabel(text=f"{'Climate'}: {climate}")
        habitability_label = arcade.gui.UILabel(text="Habitability: 100%")
        year_label = arcade.gui.UILabel(text="Year Founded: TBD")

        planet_info.add(planet_label)
        planet_info.add(climate_label)
        planet_info.add(habitability_label)
        planet_info.add(year_label)
        box3.add(planet_info, anchor_x="left")

        planet_sprite_box = arcade.gui.UIAnchorLayout(size_hint=(0.5, 1))
        #planet_sprite = PlanetSprite() # Placeholder for a sprite or image widget
        #planet_sprite_box.add(planet_sprite)
        box3.add(planet_sprite_box, anchor_x="right")

        # --- Box 4 --- Local market info

        # Import MarketGoodWidget
        from views.UI_stuff.market_gui import MarketGoodWidget
        # End import

        box4 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Local market info
        box4.with_border()
        self.grid.add(box4, row=1, column=2, row_span=2)

        frame = arcade.gui.UIBoxLayout(vertical=True, size_hint=(1, 1))
        box4.add(frame)

        # Box 4a - expensive goods
        box4a = arcade.gui.UIBoxLayout(vertical=True, size_hint=(1, 0.5), space_between=2)
        box4a.with_border(color=arcade.color.STEEL_BLUE)
        expensive_market_label = arcade.gui.UILabel(text="Expensive Goods")
        box4a.add(expensive_market_label)
        for good in self.colony.local_market.get_expensive_goods(number=5):
            #good_label = arcade.gui.UILabel(text=f"{good.name}: ${good.current_price}")
            #box4a.add(good_label)
            expensive_good_widget = MarketGoodWidget(good, self.asset_manager)
            box4a.add(expensive_good_widget)
            self.short_term_updatable_content.append(expensive_good_widget)

        # Box 4b - cheap goods
        box4b = arcade.gui.UIBoxLayout(vertical=True, size_hint=(1, 0.5), space_between=2, align="bottom")
        box4b.with_border(color=arcade.color.STEEL_BLUE)
        cheap_market_label = arcade.gui.UILabel(text="Cheap Goods")
        box4b.add(cheap_market_label)
        for good in self.colony.local_market.get_cheap_goods(number=5):
            #good_label = arcade.gui.UILabel(text=f"{good.name}: ${good.current_price}")
            #box4b.add(good_label)
            cheap_good_widget = MarketGoodWidget(good, self.asset_manager)
            box4b.add(cheap_good_widget)
            self.short_term_updatable_content.append(cheap_good_widget)

        market_label = arcade.gui.UILabel(text="Local Market")
        frame.add(market_label, anchor_y="top")
        frame.add(box4a, anchor_y="top")
        frame.add(box4b, anchor_y="bottom")

        # --- Box 5 --- Build queue
        box5 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Build queue
        box5.with_border()
        self.grid.add(box5, row=1, column=3, row_span=2)

        build_queue_label = arcade.gui.UILabel(text="Build Queue")
        box5.add(build_queue_label, anchor_y="top")


    def show_economy_tab(self):
        self.grid.clear()  # Clear previous content
        self.current_tab = "Economy"
        self.short_term_updatable_content.clear()

        self.grid = arcade.gui.UIGridLayout(size_hint=(1, 1), row_count=3, column_count=4)
        self.grid.with_background(color=arcade.color.CHARCOAL)

        # --- Box 1 --- Planet art and overview
        self.box1()

        # --- Box 2 --- Pie chart of economy sectors
        box2 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # pie chart of economy sectors
        box2.with_border()
        # Add stuff here later
        self.grid.add(box2, row=0, column=3) # Add completed box to grid

        # Box 3, 4, and 5 will be a building grid of urban, rural, and government buildings respectively

        # --- Box 3 --- Urban buildings
        box3 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Urban buildings
        box3.with_border()
        # --- Urban buildings grid ---
        urban_buildings_grid = BuildingGrid(self, "Urban", self.asset_manager)
        box3.add(urban_buildings_grid, anchor_x="center", anchor_y="center")
        self.grid.add(box3, row=1, column=0, row_span=2)

        # --- Box 4 --- Rural buildings
        box4 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Rural buildings
        box4.with_border()
        # --- Rural buildings grid ---
        rural_buildings_grid = BuildingGrid(self, "Rural", self.asset_manager)
        box4.add(rural_buildings_grid, anchor_x="center", anchor_y="center")
        self.grid.add(box4, row=1, column=1, row_span=2)

        # --- Box 5 --- Government buildings
        box5 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Government buildings
        box5.with_border()
        # --- Government buildings grid ---
        self.grid.add(box5, row=1, column=2, row_span=2)

        # --- Box 6 --- More charts and graphs of economy ---
        box6 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # More charts and stats of economy
        box6.with_border()
        # Add stuff here later
        self.grid.add(box6, row=1, column=3, row_span=2)

        # add completed grid to content frame for display
        self.content_frame.add(self.grid)

        if self.current_tab == "Summary":
            self.gdp_label.text = f"GDP: {self.colony.local_bls.statistics.get('gdp', 'N/A')}"
            self.population_label.text = f"Population: {self.colony.local_bls.statistics.get('population', 'N/A')}"
            self.stability_label.text = f"Stability: {self.colony.local_bls.statistics.get('stability', 'N/A')}"
            self.unemployment_label.text = f"Unemployment: {self.colony.local_bls.statistics.get('unemployment_rate', 'N/A')}%"

    def refresh(self, colony):
        self.colony = colony
        if self.current_tab == "Summary":
            self.gdp_label.text = f"GDP: {self.colony.local_bls.statistics.get('gdp', 'N/A')}"
            self.population_label.text = f"Population: {self.colony.local_bls.statistics.get('population', 'N/A')}"
            self.stability_label.text = f"Stability: {self.colony.local_bls.statistics.get('stability', 'N/A')}"
            self.unemployment_label.text = f"Unemployment: {self.colony.local_bls.statistics.get('unemployment_rate', 'N/A')}%"
        elif self.current_tab == "Economy":
            # Update economy tab content if needed
            pass

def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
import arcade
import arcade.gui


class PlanetInterface:
    def __init__(self, model, nation):
        self.model = model
        self.planet = None
        self.nation = nation
        self.manager = arcade.gui.UIManager()
        # Possible tabs are: Summary, Buildings, Population, ...more to come
        self.current_tab = None

        self.window = arcade.gui.UIAnchorLayout(size_hint=(0.5, 0.5))
        self.manager.add(self.window)
        self.layout = arcade.gui.UIAnchorLayout(size_hint=(1, 1))
        self.current_tab = "Summary"
        self.manager.add(self.layout)
        self.grid_frame = arcade.gui.UIAnchorLayout(size_hint=(1, 0.95), anchor_y="bottom")
        self.layout.add(self.grid_frame)

    def setup_window(self):
        top_bar = arcade.gui.UIAnchorLayout(size_hint=(1, 0.05), anchor_y="top")
        planet_label = arcade.gui.UILabel(text=f"{self.planet.name}")
        close_button = arcade.gui.UIFlatButton(text="X", anchor_x="right")
        top_bar.add(planet_label)
        top_bar.add(close_button)
        self.layout.add(top_bar)

    def update_current_tab(self, tab):
        pass

    def summary_tab(self):
        self.grid_frame.clear()
        grid = arcade.gui.UIGridLayout(size_hint=(1, 1), column_count=3, row_count=3)

        self.grid_frame.add(grid)

    def buildings_tab(self):
        pass

    def population_tab(self):
        pass

    def set_planet(self, colony):
        self.planet = colony
        self.current_tab = "Summary"


import arcade
import arcade.gui
from views.UI_stuff.gui_constructs import Progressbar2
from views.UI_stuff.planet_menu import GenericMenu


class BuildingGUI(GenericMenu):
    """
    GUI for displaying building information and management options.
    For the first draft, this will simply imitate Victora 3's building UI.
    """
    def __init__(self, asset_manager, *args, **kwargs):
        super().__init__(asset_manager=asset_manager, *args, **kwargs)
        self.building = None
        self.asset_manager = asset_manager
        self.content_frame.with_background(color=arcade.color.DARK_SLATE_GRAY)
        self.window.size_hint = (0.3, 0.6)
        self.window.center_x = 600

        self.info_column = arcade.gui.UIBoxLayout(size_hint=(1, 1), vertical=True, space_between=10)
        self.content_frame.add(self.info_column)

    def setup_content(self):
        self.info_column.clear()
        # Building Name
        self.title_label.text = self.building.name

        # --- Box 1: --- Icon, Cash reseves, staffing, and productivity ---
        box1 = arcade.gui.UIAnchorLayout(size_hint=(1, 0.2))
        box1.with_background(color=arcade.color.DARK_BLUE_GRAY)
        box1.with_border()

        icon_texture = self.asset_manager.building_icons.get(self.building.name, self.asset_manager.building_icons["default"])
        building_icon = arcade.gui.UIImage(texture=icon_texture, width=64, height=64)
        # TODO: implement progressbar class
        #staffing_bar = arcade.gui.UIProgressBar(value=self.building.get_staffing_percentage()*100, min_value=0, max_value=100, width=200, height=20)
        #cash_reserves_bar = arcade.gui.UIProgressBar(value=self.building.cash_reserves*100, min_value=0, max_value=100, width=200, height=20)
        productivity_chart = arcade.gui.UILabel(text=f"Productivity: {self.building.get_productivity():.1f}%", font_size=14)
        box1.add(building_icon, anchor_x="left", anchor_y="center", align_x=10)
        #box1.add(staffing_bar, anchor_x="center", anchor_y="center")
        #box1.add(cash_reserves_bar, anchor_x="center", anchor_y="center")
        box1.add(productivity_chart, anchor_x="right", anchor_y="center", align_x=-10)
        self.info_column.add(box1)

        # --- Box 2: --- Production Process ---
        box2 = arcade.gui.UIBoxLayout(size_hint=(1, 0.4), vertical=False)
        box2.with_background(color=arcade.color.DARK_BLUE_GRAY)
        box2.with_border()

        #production_label = arcade.gui.UILabel(text="Production Process:", font_size=16)

        # Input Goods and Wages
        input_box = arcade.gui.UIBoxLayout(size_hint=(0.5, 1), vertical=True, space_between=5)
        input_label = arcade.gui.UILabel(text="Inputs:", font_size=14)
        input_box.add(input_label)  
        for input_good, amount in self.building.input_requirements.items():
            good_icon = self.asset_manager.resource_icons.get(input_good, self.asset_manager.resource_icons["default"])
            good_widget = arcade.gui.UIBoxLayout(size_hint=(1, 0.2), vertical=False, space_between=5)
            good_widget.with_border()
            icon_image = arcade.gui.UIImage(texture=good_icon, width=32, height=32)
            good_name = arcade.gui.UILabel(text=f"{input_good}: {amount} for ${cost}", font_size=12)
            good_widget.add(icon_image)
            good_widget.add(good_name)
            input_box.add(good_widget)
        wages_label = arcade.gui.UILabel(text=f"Wages per cycle: ${self.building.calculate_wages_per_cycle():.2f}", font_size=12)
        input_box.add(wages_label)

        # Output Goods
        output_box = arcade.gui.UIBoxLayout(size_hint=(0.5, 1), vertical=True, space_between=5)
        output_label = arcade.gui.UILabel(text="Outputs:", font_size=14)
        output_box.add(output_label)
        for output_good, amount in self.building.output_products.items():
            good_icon = self.asset_manager.resource_icons.get(output_good, self.asset_manager.resource_icons["default"])
            good_widget = arcade.gui.UIBoxLayout(size_hint=(1, 0.2), vertical=False, space_between=5)
            good_widget.with_border()
            icon_image = arcade.gui.UIImage(texture=good_icon, width=32, height=32)
            good_name = arcade.gui.UILabel(text=f"{output_good}: {amount}", font_size=12)
            good_widget.add(icon_image)
            good_widget.add(good_name)
            output_box.add(good_widget)
        balance_label = arcade.gui.UILabel(text=f"Profit per cycle: ${self.building.calculate_profit_per_cycle():.2f}", font_size=12)
        output_box.add(balance_label)
        throughput_label = arcade.gui.UILabel(text=f"Throughput: {self.building.get_throughput():.1f} units/cycle", font_size=12)
        output_box.add(throughput_label)

        box2.add(input_box)
        box2.add(output_box)
        #box2.add(production_label, anchor_x="center", anchor_y="top", align_y=-10)
        self.info_column.add(box2)

        # --- Box 3: --- Ownership and Upgrades ---
        box3 = arcade.gui.UIBoxLayout(size_hint=(1, 0.2), vertical=False, space_between=10)
        box3.with_background(color=arcade.color.DARK_BLUE_GRAY)
        box3.with_border()

        owner_label = arcade.gui.UILabel(text=f"Owner: {self.building.owner.name}", font_size=14)
        upgrade_label = arcade.gui.UILabel(text=f"Upgrades: {len(self.building.upgrades)}/{self.building.max_upgrades}", font_size=14)
        box3.add(owner_label)
        box3.add(upgrade_label)
        self.info_column.add(box3)

    def open_window(self, building):
        self.building = building
        self.title_label.text = f"Building: {building.name}"
        self.setup_content()
        self.manager.enable()
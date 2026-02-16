import arcade
import arcade.gui
from views.UI_stuff.graph_widget import GraphWidget
from views.UI_stuff.planet_menu import GenericMenu

class MarketGUI(GenericMenu):
    def __init__(self, asset_manager, *args, **kwargs):
        super().__init__(asset_manager=asset_manager, *args, **kwargs)
        self.market = None
        self.asset_manager = asset_manager
        self.content_frame.with_background(color=arcade.color.DARK_SLATE_GRAY)
        self.window.size_hint = (0.25, 0.8)
        self.window.center_x = 600

        self.market_column = arcade.gui.UIBoxLayout(size_hint=(1, 1), vertical=True, space_between=2)
        self.content_frame.add(self.market_column)

    def setup_content(self):
        self.market_column.clear()
        self.icons = {}
        for good in self.market.goods.values():
            self.icons[good.name] = self.asset_manager.resource_icons.get(good.name, self.asset_manager.resource_icons["default"])

            # Add market goods widgets
            good_widget = MarketGoodWidget(good, self.asset_manager, self)
            self.market_column.add(good_widget)
            print(f"Added widget for good: {good.name}")

    def open_window(self, market):
        self.market = market
        self.title_label.text = "Market Overview"
        self.setup_content()
        self.manager.enable()

    def on_daily_update(self):
        for child in self.market_column.children:
            if isinstance(child, MarketGoodWidget):
                child.on_daily_update()


class MarketGoodWidget(arcade.gui.UIBoxLayout):
    def __init__(self, good, assets, *args, **kwargs):
        super().__init__(size_hint=(1, 0.1), vertical=False, space_between=2, *args, **kwargs)
        self.good = good
        self.assets = assets # asset manager reference
        self.icon = self.assets.get_resource_icon(good.name)
        self.with_background(color=arcade.color.DARK_BLUE_GRAY)
        self.with_border()

        self.good_label = arcade.gui.UILabel(text=f"{self.good.name}", multiline=True)
        self.good_icon = arcade.gui.UIImage(texture=self.icon, width=32, height=32)
        self.price_label = arcade.gui.UILabel(text=f"Price: {self.good.current_price}")
        #self.price_chart = GraphWidget(title=f"{self.good.name} Price History", y_label="Price", x_label="Time", max_points=50)
        self.supply_label = arcade.gui.UILabel(text=f"Supply: {self.good.supply}")
        self.demand_label = arcade.gui.UILabel(text=f"Demand: {self.good.demand}")

        self.add(self.good_label)
        self.add(self.good_icon)
        self.add(self.price_label)
        #self.add(self.price_chart)
        self.add(self.supply_label)
        self.add(self.demand_label)

    def on_daily_update(self):
        self.price_label.text = f"Price: {self.good.current_price}"
        self.supply_label.text = f"Supply: {self.good.supply}"
        self.demand_label.text = f"Demand: {self.good.demand}"
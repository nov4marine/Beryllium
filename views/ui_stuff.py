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
        self.planet_menu = PlanetMenu(self.asset_manager)
        self.left_sidebar = LeftSideBar(self.manager, self.asset_manager)
        self.right_ledger = RightLedger(self, self.manager, self.asset_manager)

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

        self.stats.add(self.standard_of_living)
        self.stats.add(self.radicals)
        self.stats.add(self.loyalists)
        self.stats.add(self.bureaucracy)
        self.stats.add(self.authority)
        self.stats.add(self.treasury)
        self.stats.add(self.tech)
        self.stats.add(self.starbases)

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
        self.gdp.text = f"GDP: {self.player_nation.gdp}"
        self.gdp_per_capita.text = f"GDP per capita: {self.player_nation.gdp_per_capita}"
        self.population.text = f"Population: {self.player_nation.population}"

        self.standard_of_living.text = self.player_nation.standard_of_living
        self.loyalists.text = self.player_nation.loyalists
        self.radicals.text = self.player_nation.radicals

        self.bureaucracy.text = self.player_nation.bureaucracy
        self.authority.text = self.player_nation.authority
        self.treasury.text = self.player_nation.treasury

    def on_daily_update(self):
        self.date.text = self.game_model.calendar.__str__()
        self.planet_menu.on_daily_update()
        self.right_ledger.update(self.player_nation)

    def show_planet_menu(self, colony):
        self.planet_menu.open_window(colony)

class GalaxyStarLabel:
    def __init__(self, body, sprite_list):
        self.body = body
        self.text = arcade.create_text_sprite(
            text=body.name,
        )
        self.text.center_x = body.x
        self.text.center_y = body.y - 40

        self.background = arcade.SpriteSolidColor(
            width=self.text.width + 10,
            height=self.text.height + 4,
            color=arcade.color.STEEL_BLUE,
            center_x=self.text.center_x,
            center_y=self.text.center_y,
        )
        sprite_list.append(self.background)
        sprite_list.append(self.text)

    def update(self, camera_zoom):
        scale_factor = 1 / camera_zoom
        self.text.scale = scale_factor
        self.background.scale = scale_factor


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

class LeftSideBar:
    def __init__(self, manager, asset_manager):
        self.manager = manager
        self.assets = asset_manager
        self.collapsed = True
        self.root = self.manager.add(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.collapsed_panel = arcade.gui.UIBoxLayout(size_hint=(0.04, 0.5))
        self.collapsed_panel.with_background(color=arcade.color.DARK_BLUE_GRAY)
        # add widgets to collapsed panel
        self.collapsed_button = arcade.gui.UIFlatButton(size_hint=(1, 1))
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


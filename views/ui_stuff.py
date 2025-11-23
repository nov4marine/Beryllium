import arcade
import arcade.gui
from views.UI_stuff.planet_menu import PlanetMenu, BuildingGUI
from views.UI_stuff.market_gui import MarketGUI


class PersistentUI:
    """Baiscally the primary GUI that is always on screen, or has elements that persist across views"""
    def __init__(self, game_model, asset_manager):
        self.game_model = game_model
        self.asset_manager = asset_manager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.player_nation = None

        # --- Sub-Components ---
        # all of these must be added to both draw and update
        self.planet_menu = PlanetMenu(self, self.asset_manager)
        self.building_gui = BuildingGUI(self, self.asset_manager)
        self.left_sidebar = LeftSideBar(self, self.manager, self.asset_manager)
        self.right_ledger = RightLedger(self, self.manager, self.asset_manager)
        
        self.market_gui = MarketGUI(self.asset_manager)

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
        self.building_gui.draw()
        self.market_gui.draw()

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
        self.building_gui.on_daily_update()
        self.right_ledger.update(self.player_nation)
        self.market_gui.on_daily_update()

    def show_planet_menu(self, colony):
        self.planet_menu.open_window(colony)

    def show_market_gui(self):
        self.market_gui.open_window(self.player_nation.national_market)

    def show_building_gui(self, building):
        self.building_gui.open_window(building)

class GalaxyStarLabel:
    def __init__(self, body, text_sprite_list, bg_sprite_list):
        self.body = body
        self.color = (arcade.color.DARK_GREEN)
        self.text = arcade.create_text_sprite(
            text=body.name,
        )
        self.text.center_x = body.x
        self.text.center_y = body.y - 40

        self.background = arcade.SpriteSolidColor(
            width=self.text.width + 10,
            height=self.text.height + 4,
            color=self.color,
            center_x=self.text.center_x,
            center_y=self.text.center_y,
        )
        bg_sprite_list.append(self.background)
        text_sprite_list.append(self.text)

    def update(self, camera_zoom):
        scale_factor = 1 / camera_zoom
        self.background.scale = scale_factor
        self.text.scale = scale_factor

# Solar system UI elements and sprites
class CelestialBodySprite(arcade.SpriteCircle):
    def __init__(self, body):
        super().__init__(body.size, body.color)
        self.model_reference = body

    def update(self, delta_time: float = 1/60):
        body_pos = self.model_reference.get_position()
        self.center_x = body_pos[0]
        self.center_y = body_pos[1]

class CelestialBodyLabel:
    def __init__(self, body, spritelist):
        self.body = body
        self.color = (arcade.color.CHARCOAL)
        self.text = arcade.Text(
            text=body.name,
            #font_size=16,
            x=0,
            y=0,
        )
        texture_size = (
            int(self.text.content_width + 20), 
            int(self.text.content_height + 10)
        )
        self.text.anchor_x = "center"
        self.text.anchor_y = "center"
        self.text.x = texture_size[0] / 2
        self.text.y = texture_size[1] / 2 
        self.texture = arcade.Texture.create_empty(body.name, size=texture_size)
        
        self.sprite = arcade.Sprite(
            self.texture,
            center_x=body.x,
            center_y=body.y - 40,
        )

        spritelist.append(self.sprite)
        with spritelist.atlas.render_into(self.texture) as fbo:
            fbo.clear(color=self.color)
            arcade.draw_lbwh_rectangle_outline(
                left=0,
                bottom=0,
                width=texture_size[0],
                height=texture_size[1],
                color=arcade.color.WHITE,
                border_width=4,
            )
            self.text.draw()

    def update(self, camera_zoom):
        scale_factor = 1 / camera_zoom
        self.sprite.scale = scale_factor
        self.sprite.center_y = self.body.y - (40 * scale_factor)


class PlanetLabel(CelestialBodyLabel):
    def __init__(self, body, spritelist):
        self.body = body
        position = body.get_position()
        body.x = position[0]
        body.y = position[1]
        super().__init__(body, spritelist)

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


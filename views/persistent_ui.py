import arcade
import arcade.gui
#from views.UI_stuff.planet_menu import PlanetMenu, BuildingGUI
#from views.UI_stuff.market_gui import MarketGUI
from views.ui_elements.hud_elements import TopBar

"""
Master UI class that contains all the elements that persist across views, such as the resource bar, date, and any other HUD elements.
Hook this up to the calendar and keep it persistent outside of views. 
Core things to remember/do: 
1. Keep route all GUI updates through this class, and have the calendar update it daily ONLY. (maybe per frame later)
2. The strategy for now is to create the framework/class for every UI menu upon initialization, and thus be able to be created without reference to what it'll be displaying.
2.5. Also every menu must have a on_open and/or refresh method for changing which object the menu is displaying (eg which planet or building)
3. I need to learn how to make a scrollable gui container for a shitload of stuff.

4. Using the new branch mechanic of git, learn to make a new branch for each game feature, and do not merge until the feature is robust (but partially implemented is fine).
4.5 Always lean on the side of simplicity and UNDER-complicating. My code is full of 20 half baked, overly ambitious features that don't play well together.

5. I also need to reorganize the files sometime. This file being named ui_stuff is already bad, but worse because the folder is also named ui_stuff.
"""

class PersistentUI:
    """
    Baiscally the primary GUI that is always on screen, or has elements that persist across views.
    Serves as a sort of controller or container or manager for all various UI components, such as the resource bar, the planet menu, the market menu, and so on.
    Also serves as the primary observer of the calendar, and thus the main conduit for updating the UI based on the passage of time.
    #TODO: refactor calendar to be pauseable, but also still update UI changes even when paused. A core part of paradox games is pausing to do a bunch of micro.
    """
    def __init__(self, game_model, asset_manager):
        self.game_model = game_model
        self.calendar = game_model.calendar
        self.asset_manager = asset_manager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.player_nation = None

        # --- Sub-Components ---
        # all of these must be added to draw
        #self.planet_menu = PlanetMenu(self.asset_manager)
        #self.building_gui = BuildingGUI(self, self.asset_manager)
        self.top_bar = TopBar(self, self.asset_manager)
        #self.left_sidebar = LeftSideBar(self, self.manager, self.asset_manager)
        #self.right_ledger = RightLedger(self, self.manager, self.asset_manager)
        #TODO: refactor to consolidate things like the resource bar/ top_bar into a subcomponent. This manager should not directly handle individual UI elements.
        
        #self.market_gui = MarketGUI(self.asset_manager)

        # --- Root UI Layout which all subcomponents are added to ---
        self.root = self.manager.add(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        # --- Create HUD components ---
        self.root.add(self.top_bar, anchor_y="top")
        #self.root.add(self.left_sidebar, anchor_x="left", anchor_y="center")
        #self.root.add(self.right_ledger, anchor_x="right", anchor_y="center")

    def set_player_nation(self, nation):
        self.player_nation = nation
        self.top_bar.player_nation = nation

    def draw(self):
        self.manager.draw()

    def on_monthly_update(self):
        pass

    def on_daily_update(self):
        self.top_bar.on_daily_update()
        #self.planet_menu.on_daily_update()
        #self.building_gui.on_daily_update()
        #self.right_ledger.update(self.player_nation)

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

import math

def draw_dashed_circle_outline(center_x, center_y, radius, color, border_width=2, num_dashes=100, dash_fraction=0.5):
    angle_per_dash = 2 * math.pi / num_dashes
    dash_angle = angle_per_dash * dash_fraction
    for i in range(num_dashes):
        start_angle = i * angle_per_dash
        end_angle = start_angle + dash_angle
        x1 = center_x + radius * math.cos(start_angle)
        y1 = center_y + radius * math.sin(start_angle)
        x2 = center_x + radius * math.cos(end_angle)
        y2 = center_y + radius * math.sin(end_angle)
        arcade.draw_line(x1, y1, x2, y2, color, border_width)

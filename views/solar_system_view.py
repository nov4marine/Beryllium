import arcade
import arcade.gui
from views.ui_stuff import PersistentUI, PlanetLabel, CelestialBodyLabel, PlanetLabel, CelestialBodySprite



class SolarSystemView(arcade.View):
    def __init__(self, game_model, galaxy_star, galaxy_view):
        super().__init__()
        self.model = game_model
        self.solar_system = galaxy_star.solar_system
        self.galaxy_view = galaxy_view

        # Controller Elements
        self.solarsystemui_manager = arcade.gui.UIManager()
        self.persistent_ui = self.window.persistent_ui
        self.asset_manager = self.window.asset_manager
        self.calendar = self.window.calendar
        self.selected_sprite = None

        self.solar_system_background = self.asset_manager.ui_art.get("solar_system_background")

        self.celestial_bodies = arcade.SpriteList()
        self.fleets = arcade.SpriteList()

        self.orbit_visuals = []
        self.planet_labels = []
        self.planet_label_sprites = arcade.SpriteList()

        self.map_camera = arcade.Camera2D()
        self.hud_camera = arcade.Camera2D()

        # Variables to track WASD for panning
        self.pan_left = False
        self.pan_right = False
        self.pan_up = False
        self.pan_down = False

        self.background_color = arcade.color.SMOKY_BLACK

        self.setup()

        self.root = self.solarsystemui_manager.add(arcade.gui.UIAnchorLayout())

    def on_show_view(self):
        # --- UI stuff specific to Solar System View ---
        self.root.clear()
        self.solarsystemui_manager.enable()
        system_card = arcade.gui.UIAnchorLayout(size_hint=(0.3, 0.05))
        system_card.with_background(color=arcade.color.ANDROID_GREEN)
        self.root.add(system_card, anchor_x="center", anchor_y="bottom")

        system_label = arcade.gui.UILabel(text=f"Star System: {self.solar_system.name}")
        return_to_galaxy = arcade.gui.UIFlatButton(text="Return to Galaxy View")

        system_card.add(system_label, anchor_x="left")
        system_card.add(return_to_galaxy, anchor_x="right")

        @return_to_galaxy.event("on_click")
        def on_click_return_to_galaxy(event):
            print("return to galaxy clicked!")
            self.window.show_view(self.galaxy_view)

    def on_hide_view(self):
        self.solarsystemui_manager.disable()
        #self.solarsystemui_manager.remove(self.root)

    def setup(self):
        # --- Celestial Body Sprite Setup ---
        for body in self.solar_system.bodies:
            celestial_sprite = CelestialBodySprite(body)
            self.celestial_bodies.append(celestial_sprite)

        # --- Planet Labels ---
        for celestial_body_model in self.solar_system.bodies:
            label = PlanetLabel(celestial_body_model, spritelist=self.planet_label_sprites)
            self.planet_labels.append(label)


    def pan_map_camera(self, delta_time):
        pan_speed = 80 / self.map_camera.zoom
        current_position = self.map_camera.position

        new_x = current_position.x
        new_y = current_position.y

        if self.pan_up:
            new_y += pan_speed
        if self.pan_down:
            new_y -= pan_speed
        if self.pan_left:
            new_x -= pan_speed
        if self.pan_right:
            new_x += pan_speed

        self.map_camera.position = (new_x, new_y)

    def reset(self):
        """Reset the game to the initial state."""
        # Do changes needed to restart the game here if you want to support that
        pass

    def on_draw(self):
        self.clear()
        # --- Solar System Background ---
        background_rect = arcade.LBWH(
            left=0,
            bottom=0,
            width=self.window.width,
            height=self.window.height,
        )
        arcade.draw.draw_texture_rect(
            texture=self.solar_system_background,
            rect=background_rect,
        )

        self.map_camera.use()
        camera_zoom = self.map_camera.zoom
        # --- Draw Solar System Celestials ---
        # Draw faint orbital rings for orbiting bodies
        for body in self.solar_system.bodies:
            if body.parent:
                parent_pos = body.parent.get_position()
                arcade.draw_circle_outline(
                    color=(100, 100, 140, 180),  # Faint blue-gray color
                    center_x=(int(parent_pos[0])),
                    center_y=(int(parent_pos[1])),
                    radius=int(body.radius),
                    border_width=1/camera_zoom
                )
            else:
                pass
        # Draw all bodies (stars, planets, moons, asteroids)
        self.celestial_bodies.draw()
        
        if camera_zoom > 0.5:
            #for label in self.planet_labels:
                #label.update(camera_zoom)
            self.planet_label_sprites.draw()

        self.hud_camera.use()
        self.solarsystemui_manager.draw()
        self.persistent_ui.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        # --- Process Calendar Time ---
        self.calendar.update(delta_time)

        self.celestial_bodies.update()
        self.pan_map_camera(delta_time)

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.W:
            self.pan_up = True
        elif key == arcade.key.S:
            self.pan_down = True
        elif key == arcade.key.A:
            self.pan_left = True
        elif key == arcade.key.D:
            self.pan_right = True

    def on_key_release(self, key, key_modifiers):
        if key == arcade.key.W:
            self.pan_up = False
        elif key == arcade.key.S:
            self.pan_down = False
        elif key == arcade.key.A:
            self.pan_left = False
        elif key == arcade.key.D:
            self.pan_right = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        # Convert screen to world coordinates
        world_pos = self.map_camera.unproject((x, y))
        world_x = world_pos.x
        world_y = world_pos.y

        # Check if a planet was clicked
        for sprite in self.celestial_bodies:
            # Only open menu for planets (not stars, asteroids, etc.)
            body = sprite.model_reference
            print(f"Clicked on planet: {body.name}")
            if hasattr(body, 'colony') and body.colony:
                if sprite.collides_with_point((world_x, world_y)):
                    self.persistent_ui.show_planet_menu(body.colony)
                    return

        for label in self.planet_label_sprites:
            if label.collides_with_point((world_x, world_y)):
                print(f"Clicked on label: {label.body.name}")
                return


    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.map_camera.zoom *= 1.1 if scroll_y > 0 else 0.9
        self.map_camera.zoom = max(0.01, min(self.map_camera.zoom, 4.0))  # Limit zoom level

        for label in self.planet_labels:
            label.update(self.map_camera.zoom)

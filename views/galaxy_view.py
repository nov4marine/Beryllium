import arcade
import arcade.gui
from views.solar_system_view import SolarSystemView
from views.persistent_ui import GalaxyStarLabel, CelestialBodyLabel

from pyglet.graphics import Batch

from scipy.spatial import Voronoi


class GalaxyView(arcade.View):
    def __init__(self, game_model):
        super().__init__()
        self.model = game_model
        self.persistent_ui = self.window.persistent_ui
        self.galaxy = self.model.galaxy

        self.world_ui_manager = arcade.gui.UIManager()
        # Controller Elements
        self.asset_manager = self.window.asset_manager
        self.calendar = self.window.calendar
        self.selected_sprite = None

        # Dictionary to hold different map overlays and map modes
        self.maps = {
            "sovereignty": SovereigntyOverlay(self.galaxy)
        }

        # --- Load Assets ---
        self.galaxy_map_background = self.asset_manager.ui_art.get("galaxy_background")
        self.galaxy_disk_texture = self.asset_manager.ui_art.get("m51_4k")

        # --- Sprite Lists ---
        self.star_sprites = arcade.SpriteList()
        self.star_clickboxes = arcade.SpriteList()

        self.fleet_sprites = arcade.SpriteList()
        self.fleet_clickboxes = arcade.SpriteList()

        self.hyperlane_visuals = []
        self.star_labels = []
        self.star_label_sprites = arcade.SpriteList()

        # Cameras
        self.map_camera = arcade.camera.Camera2D()
        self.hud_camera = arcade.camera.Camera2D()
        #self.world_ui_manager.camera = self.map_camera

        # Variables to track WASD for panning
        self.pan_left = False
        self.pan_right = False
        self.pan_up = False
        self.pan_down = False

        self.setup()

        # If you have sprite lists, you should create them here,
        # and set them to None

    def on_show_view(self):
        self.world_ui_manager.enable()
        self.selected_sprite = None

    def setup(self):
        # --- Star Sprite Setup ---
        for star_model in self.galaxy.galaxy_stars:
            star_sprite = arcade.SpriteCircle(radius=star_model.radius, color=star_model.color, soft=True)
            star_sprite.center_x = star_model.x
            star_sprite.center_y = star_model.y
            star_sprite.model_reference = star_model
            self.star_sprites.append(star_sprite)

            star_clickbox = arcade.SpriteCircle(star_model.radius * 2, arcade.color.TRANSPARENT_BLACK)
            star_clickbox.center_x = star_model.x
            star_clickbox.center_y = star_model.y
            star_clickbox.model_reference = star_model
            self.star_clickboxes.append(star_clickbox)

        # --- Hyperlane Setup ---
        # We will build a single list of all points for all hyperlanes.
        # Each pair of points in the list defines a line.
        # Iterate through your list of (start, end) tuples.
        for start_point, end_point in self.galaxy.hyperlanes:
            # Add the start point as a tuple (x, y)
            self.hyperlane_visuals.append((start_point.x, start_point.y))

            # Add the end point as a tuple (x, y)
            self.hyperlane_visuals.append((end_point.x, end_point.y))

        # --- Map Overlays ---
        self.maps["sovereignty"].calculate_galaxy_map()

        # Prepare world-anchored star label data (not UI widgets)
        for star_model in self.galaxy.galaxy_stars:
            label = CelestialBodyLabel(star_model, spritelist=self.star_label_sprites)
            self.star_labels.append(label)

    def pan_map_camera(self, delta_time):
        pan_speed = 100
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

    def on_draw(self):
        self.clear()
        # --- Galaxy Background ---
        arcade.draw.draw_texture_rect(
            texture=self.galaxy_map_background,
            rect=arcade.LBWH(
                left=0,
                bottom=0,
                width=self.window.width,
                height=self.window.height,
            )
        )

        self.map_camera.use()  # Map camera to draw all game world elements
        camera_zoom = self.map_camera.zoom
        # All camera dependent drawing goes here:

        # --- Galaxy Disk ---
        disk_multiplier = 1.1
        disk = arcade.LBWH(
            left=-self.galaxy.galaxy_size * disk_multiplier,
            bottom=-self.galaxy.galaxy_size * disk_multiplier,
            width=self.galaxy.galaxy_size * 2 * disk_multiplier,
            height=self.galaxy.galaxy_size * 2 * disk_multiplier,
        )
        arcade.draw.draw_texture_rect(
            texture=self.galaxy_disk_texture,
            rect=disk,
            alpha=140,
        )

        # --- Map Overlays ---
        self.maps["sovereignty"].draw_voronoi_map()

        # --- Hyperlanes ---
        arcade.draw_lines(
            self.hyperlane_visuals,
            color=(120, 180, 225, 180),
            line_width=1/camera_zoom
        )

        # --- Stars ---
        self.star_sprites.draw()
        self.star_clickboxes.draw()
        for clickbox in self.star_clickboxes:
            clickbox.radius = clickbox.model_reference.radius * 2 / camera_zoom

        # --- Everything above this line is background stuff that should not be occluded by active elements ---
        # --- World-Anchored Labels (drawn manually, not UI widgets) ---
        if camera_zoom > 0.5:  # Only show labels when zoomed in
            for label in self.star_labels:
                label.update(camera_zoom)
            self.star_label_sprites.draw()

        # --- Selection Highlight ---
        if self.selected_sprite:
            arcade.draw_circle_outline(
                self.selected_sprite.center_x,
                self.selected_sprite.center_y,
                self.selected_sprite.radius,
                arcade.color.YELLOW,
                border_width=3,
            )

        # --- Static UI Elements ---
        self.hud_camera.use()  # Switch to a camera that doesn't move
        self.world_ui_manager.draw()
        self.persistent_ui.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        # --- Process Calendar Time ---
        self.calendar.update(delta_time)

        self.star_clickboxes.update(delta_time)
        self.star_sprites.update(delta_time)
        self.star_label_sprites.update(delta_time)
        if self.selected_sprite in self.star_clickboxes:
            solar_system_view = SolarSystemView(
                game_model=self.model,
                galaxy_star=self.selected_sprite.model_reference,
                galaxy_view=self
            )
            self.window.show_view(solar_system_view)
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
        print(f"selected sprite: {self.selected_sprite}")
        if self.selected_sprite:
            self.selected_sprite = None

        # Unproject screen coordinates to world coordinates
        world_pos = self.map_camera.unproject((x, y))
        world_x = world_pos.x
        world_y = world_pos.y

        for fleet in self.fleet_clickboxes:
            if fleet.collides_with_point((world_x, world_y)):
                self.selected_sprite = fleet
                return

        for star in self.star_clickboxes:
            if star.collides_with_point((world_x, world_y)):
                self.selected_sprite = star
                return

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.map_camera.zoom *= 1.1 if scroll_y > 0 else 0.9
        self.map_camera.zoom = max(0.1, min(self.map_camera.zoom, 5.0))  # Limit zoom level


class SovereigntyOverlay:
    def __init__(self, galaxy):
        self.galaxy = galaxy
        self.vor = None
        self.stars = []
        self.owned_star_names = set()
        self.shape_cache = None  # This will hold our cached shapes

    def calculate_galaxy_map(self):
        # Use all stars for Voronoi
        self.stars = list(self.galaxy.galaxy_stars)
        self.owned_star_names = {star.name for star in self.stars if star.owner is not None}

        if len(self.stars) < 2:
            self.vor = None
            self.shape_cache = None
            return

        points = [(star.x, star.y) for star in self.stars]
        self.vor = Voronoi(points)

        # --- Build the shape cache ---
        shape_list = arcade.shape_list.ShapeElementList()
        for i, star in enumerate(self.stars):
            region_index = self.vor.point_region[i]
            if region_index == -1:
                continue

            region = self.vor.regions[region_index]
            if not region or -1 in region:
                continue  # Skip infinite or empty regions

            vertices_np = self.vor.vertices[region]
            vertices = [tuple(v) for v in vertices_np]

            if star.name in self.owned_star_names:
                color = (*star.owner.color[:3], 100)  # RGBA with transparency
            else:
                continue  # Don't add unowned cells to the cache

            # Create a Shape for this polygon and add to the list
            shape = arcade.shape_list.create_polygon(vertices, color)
            shape_list.append(shape)

        self.shape_cache = shape_list

    def draw_voronoi_map(self):
        if self.shape_cache:
            self.shape_cache.draw()

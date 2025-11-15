import arcade
from pathlib import Path
class AssetManager:
    """
    A class to manage game assets like images and sounds.
    """
    def __init__(self):
        self.paths = {
            "ui art": Path("assets/ui_art"),
            "ui icons": Path("assets/ui_icons"),
            "celestial bodies": Path("assets/celestial_bodies"),
            "male portraits": Path("assets/portraits/male_filtered"),
            "female portraits": Path("assets/portraits/female_filtered"),
            "building_icons": Path("assets/ui_icons/buildings"),
            "resource_icons": Path("assets/ui_icons/resources"),
        }


        #self.images  = self.load_images()
        self.portraits = self.load_portraits()
        self.ui_art = self.load_ui_art()
        self.ui_icons = self.load_ui_icons()

        self.building_icons = self.load_building_icons()
        self.resource_icons = self.load_resource_icons()

        self.sounds = {} # Sounds will almost certainly be broken up into categories later
        self.music = {} # Music will also be broken up into categories later

        self.placeholder_image = self.ui_art["default"]
    
    def load_ui_art(self):
        """
        Load UI art from the assets directory.
        """
        ui_art = {}
        assets_path = self.paths["ui art"]
        for image_file in assets_path.glob("*.png"):
            image_name = image_file.stem
            image_name = image_name.lower()
            ui_art[image_name] = arcade.load_texture(str(image_file))
        return ui_art
    
    def load_ui_icons(self):
        """
        Load UI icons from the assets directory.
        """
        ui_icons = {}
        assets_path = self.paths["ui icons"]
        for icon_file in assets_path.glob("*.png"):
            icon_name = icon_file.stem
            icon_name = icon_name.lower()
            ui_icons[icon_name] = arcade.load_texture(str(icon_file))
        return ui_icons
    
    def load_building_icons(self):
        """
        Load UI icons from the assets directory.
        """
        building_icons = {}
        assets_path = self.paths["building_icons"]
        for icon_file in assets_path.glob("*.png"):
            icon_name = icon_file.stem
            icon_name = icon_name.lower()
            building_icons[icon_name] = arcade.load_texture(str(icon_file))
        return building_icons
    
    def load_resource_icons(self):
        """
        Load resource icons from the assets directory.
        """
        resource_icons = {}
        assets_path = self.paths["resource_icons"]
        for icon_file in assets_path.glob("*.png"):
            icon_name = icon_file.stem
            icon_name = icon_name.lower()
            resource_icons[icon_name] = arcade.load_texture(str(icon_file))
        return resource_icons
    
    def load_portraits(self):
        """
        Load species portraits from the assets directory.
        """
        portraits = {}
        assets_path = self.paths["female portraits"]
        for portrait in list(assets_path.glob("*.png"))[:10]:
            portrait_name = portrait.stem
            portraits[portrait_name] = arcade.load_texture(str(portrait))
        print(f"Loaded {len(portraits)} portraits.")
        return portraits

    def load_image(self, name, path):
        self.images[name] = arcade.load_texture(path)

    def get_image(self, name):
        return self.images.get(name)

    def load_sound(self, name, path):

        self.sounds[name] = arcade.load_sound(path)

    def get_sound(self, name):
        return self.sounds.get(name)

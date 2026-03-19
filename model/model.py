from model.world.galaxy import Galaxy
from model.world.calendar import Calendar

from model.architect import Architect
from model.registry import Registry


class GameModel:
    def __init__(self):
        # --- Core Game Attributes ---
        self.calendar = Calendar(self)

        self.registry = Registry
        self.architect = Architect(self.registry)

        # --- Major Game Entities ---
        self.galaxy = Galaxy()
        self.nations = []
        self.player_nation = None
        # Future class to log units, tech, star systems, etc.?
        self.buildings = None
        self.technologies = None

        # --- Player and AI ---
        self.player_nation = None
        self.selected_object = None
        self.current_solar_system = None

        # --- Configuration/Rules? (can be loaded from data files) ---
        # self.game_rules = data.load_game_rules() # Example: difficulty, game length, resource types

    def initialize_new_game(self):
        """Game setup"""
        self.architect.generate_galaxy_with_stars()
        self.galaxy.sync_stars()
        self.calendar.add_daily_observer(self.galaxy)
        self.player_nation = self.architect.build_nation("UNE")

        system = self.galaxy.pick_unowned_system()
        new_homeworld = system.pick_homeworld_candidate()

    def initialize_new_game2(self):
        """TODO: A simplified new game initialization for testing purposes,
        and to serve as a template for future refactoring. Currently unused"""
        # 1. Pick a random unowned solar system
        system = self.galaxy.pick_unowned_system()
        # 2. Pick a planet in that system
        planet = system.pick_homeworld_candidate()
        # 3. Create the player nation
        nation = Nation("Player Nation")
        # 4. Assign the planet as the capital
        nation.setup_capital(planet)
        # 5. Mark system and planet as owned
        system.owner = nation
        planet.owner = nation
        # 6. Add to model
        self.player_nation = nation
        self.galaxy.nations.append(nation)
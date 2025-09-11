from model.world.galaxy import Galaxy
from model.politics.nation import Nation


class GameModel:
    def __init__(self):
        # --- Core Game Attributes ---
        self.current_date = 0
        self.game_paused = False
        self.game_speed = 1.0

        # --- Major Game Entities ---
        self.galaxy = None
        self.nations = []
        self.player_nation = None
        # Future class to log units, tech, star systems, etc.?

        # --- Player and AI ---
        self.player_nation = None
        self.selected_object = None
        self.current_solar_system = None

        # --- Configuration/Rules? (can be loaded from data files) ---
        # self.game_rules = data.load_game_rules() # Example: difficulty, game length, resource types

    def initialize_new_game(self):
        """Transition from the menus to actual gameplay in the world."""
        print("Initializing new game...")

        self.galaxy = Galaxy()

        # Setup Nations 
        self.player_nation = Nation(name="UNE")
        self.nations.append(self.player_nation)

        # Add AI Empires

        # --- Deploy nations ---
        self.galaxy.deploy_nations(self.nations)
        for nation in self.nations:
            nation.initialize_nation()

    def update(self, delta_time):
        """Update the game state."""
        pass

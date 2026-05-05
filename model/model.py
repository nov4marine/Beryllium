from model.world.galaxy import Galaxy
from model.politics.nation import Nation
from model.world.calendar import Calendar

from model.managers.colony_managers import *

class GameModel:
    def __init__(self):
        # --- Core Game Attributes ---
        self.calendar = Calendar(self)
        self.game_paused = False

        # --- Major Game Entities ---
        self.galaxy = None
        self.nations = []
        # Future class to log units, tech, star systems, etc.?

        # --- Player and AI ---
        self.player_nation = None

        # --- Configuration/Rules? (can be loaded from data files) ---
        # self.game_rules = data.load_game_rules() # Example: difficulty, game length, resource types

        # --- ECS Commanders/Processors/Managers... whatever you want to call them ---
        # --- Colony level 1st for some reason ---
        self.labor_market = LaborManager()
        self.building_manager = BuildingManager()
        self.financial_manager = FinancialManager()
        self.market_manager = MarketManager()

    def on_monthly_update(self):
        for nation in self.nations:
            for colony in nation.colony:
                self.labor_market.run_market(colony)
                self.building_manager.produce(colony)
                self.financial_manager.pay_wages(colony)
                self.financial_manager.process_consumption(colony)
                self.market_manager.update_prices(colony)
            print(f"nation: {nation} monthly tick successfully completed.")



    def initialize_new_game(self):
        """Transition from the menus to actual gameplay in the world."""
        print("Initializing new game...")

        self.galaxy = Galaxy()
        # Add the galaxy to receive calendar updates both daily and monthly
        self.calendar.add_daily_observer(self.galaxy)
        self.calendar.add_monthly_observer(self.galaxy)
        self.calendar.add_regular_observer(self.galaxy)

        # Setup Nations 
        self.player_nation = Nation(name="UNE")
        self.nations.append(self.player_nation)

        for nation in self.nations:
            self.calendar.add_daily_observer(nation)
            self.calendar.add_monthly_observer(nation)

        # Add AI Empires

        # --- Deploy nations ---
        self.galaxy.deploy_nations(self.nations)
        #for nation in self.nations:
            #nation.initialize_nation()
    
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

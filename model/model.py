from model.world.galaxy import Galaxy
from model.politics.nation import Nation
from model.world.calendar import Calendar

from model.managers.colony_managers import *
from model.managers.utilities import *

from model.economy.colony import *
from model.data_templates.buildings import *
from model.data_templates.pop import *

import random

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
        self.session_manager = SessionManager()
        self.labor_market = LaborManager()
        self.building_manager = BuildingManager()
        self.financial_manager = FinancialManager()
        self.market_manager = MarketManager()
        #self.orbital_manager = OrbitManager()

    def on_monthly_update(self):
        print("starting update...")
        for nation in self.nations:
            for colony in nation.colony:
                self.labor_market.run_market(colony)
                self.building_manager.produce(colony)
                self.financial_manager.pay_wages(colony)
                self.financial_manager.process_consumption(colony)
                self.market_manager.update_prices(colony)
        print("monthly tick successfully completed.")

    def initialize_new_game_3(self):
        """
        Step 1. Spawn x number of nations
        step 2. select x unowned systems (for now just random)
        step 3. modify each respective solar system to meet homeworld conditions (For now just capital planet)
        step 4. spawn capital colony.
        """
        self.galaxy = Galaxy()
        self.player_nation = Nation("UNE")
        starting_system = random.choice(self.galaxy.solar_systems)
        homeworld_candidates = [body for body in starting_system.bodies if body.body_type == "planet"]
        homeworld = random.choice(homeworld_candidates)
        # Modify
        homeworld.planet_type = "rocky"
        # unpack
        self.setup_capital(homeworld, self.player_nation)

    def setup_capital(self, planet, owner):
        planet.colony = Colony(name=planet.name, owner=owner)
        colony = planet.colony
        print(f"Capital deploying on planet {planet.name}. Nation is {colony.owner}")
        
        # Define the starting manifest for a capital colony
        # Format: "Prototype Name": Starting Levels
        starting_layout = {
            "Mineral Extractor": 3,
            "Energy Plant": 3,
            "Farm": 3,
            "City District": 3,
            "Research Lab": 2,
            "Factory": 2,
            "Foundry": 2,
            "Holo-Theater": 2
        }

        # 1. Initialize Buildings from Prototypes
        for name, levels in starting_layout.items():
            if name in BUILDING_PROTOTYPES:
                # Create a unique instance for this colony
                new_building = copy.deepcopy(BUILDING_PROTOTYPES[name])
                new_building.levels = levels
                new_building.cash_reserves = 1000.0  # Initial liquidity seed
                
                # Store in the dictionary
                colony.buildings[name] = new_building
            else:
                print(f"Warning: {name} not found in BUILDING_PROTOTYPES")

        # 2. Initial Population Setup
        # This loop is now cleaner because we iterate through the dictionary values
        for building in colony.buildings.values():
            for job in building.jobs:
                # Create a base population for every job type
                pop_size = 10_000
                new_pop = Pop(size=pop_size)
                
                # Link the Pop and the Job
                job.employees += pop_size
                new_pop.job = job
                colony.pops.append(new_pop)

        total_population = sum(pop.size for pop in colony.pops)
        print(f"Colony {colony.name} initialized with {len(colony.buildings)} buildings and {total_population} pops.")

    def setup_capital_test(self, planet, owner):
        """Method for testing labor market and pop splitting logic. Spawns a capital colony with 1.2 people per job, initially at 0% employment."""
        planet.colony = Colony(name=planet.name, owner=owner)
        colony = planet.colony
        print(f"Capital deploying on planet {planet.name}. Nation is {colony.owner}")
        
        # Define the starting manifest for a capital colony
        # Format: "Prototype Name": Starting Levels
        starting_layout = {
            "Mineral Extractor": 3,
            "Energy Plant": 3,
            "Farm": 3,
            "City District": 3,
            "Research Lab": 2,
            "Factory": 2,
            "Alloy Foundry": 2,
            "Holo-Theater": 2
        }

        # 1. Initialize Buildings from Prototypes
        for name, levels in starting_layout.items():
            if name in BUILDING_PROTOTYPES:
                # Create a unique instance for this colony
                new_building = copy.deepcopy(BUILDING_PROTOTYPES[name])
                new_building.levels = levels
                new_building.cash_reserves = 1000.0  # Initial liquidity seed
                
                # Store in the dictionary
                colony.buildings[name] = new_building
            else:
                print(f"Warning: {name} not found in BUILDING_PROTOTYPES")

        # 2. Initial Population Setup
        total_pops = 0
        total_buildings = len(colony.buildings.values())
        for i in range(total_buildings):
            total_pops += 12000

        new_pop = Pop(size=total_pops)
        colony.pops.append(new_pop)

        # 3. Stabilize the Economy
        # Run a few ticks to populate the 'Market on Credit' and local statistics

        total_population = sum(pop.size for pop in colony.pops)
        print(f"Colony {colony.name} initialized with {len(colony.buildings)} buildings and {total_population} pops.")


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
    

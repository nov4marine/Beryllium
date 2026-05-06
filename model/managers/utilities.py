import copy
from model.data_templates.buildings import *

class SessionManager:
    """Contains methods for setting up a new game"""
    @staticmethod
    def setup_capital(colony):
        print(f"Capital deploying on planet {colony.planet.name}. Nation color is {colony.owner.color}")
        
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
        # This loop is now cleaner because we iterate through the dictionary values
        for building in colony.buildings.values():
            for job in building.jobs:
                # Create a base population for every job type
                pop_size = 10_000
                new_pop = Pop(colony, size=pop_size)
                
                # Link the Pop and the Job
                job.employees += pop_size
                new_pop.current_job = job
                colony.pops.append(new_pop)

        # 3. Stabilize the Economy
        # Run a few ticks to populate the 'Market on Credit' and local statistics
        for _ in range(2):
            colony.on_monthly_update()

        total_population = sum(pop.size for pop in colony.pops)
        print(f"Colony {colony.name} initialized with {len(colony.buildings)} buildings and {total_population} pops.")
from model.world.galaxy import Galaxy
from model.politics.nation import Nation
from model.world.calendar import Calendar


class GameModel:
    """The core game model, containing all major game entities and managing the game state."""
    def __init__(self):
        # --- Core Game Attributes ---
        self.calendar = Calendar(self)

        # --- Major Game Entities ---
        self.galaxy = None
        self.nations = [] # List of all nations in the game
        self.player_nation = None
        # Future class to log units, tech, star systems, etc.?

        # --- Player and AI ---
        self.player_nation = None

        # --- Configuration/Rules? (can be loaded from data files) ---
        # self.game_rules = data.load_game_rules() # Example: difficulty, game length, resource types

    def initialize_new_game(self):
        """Transition from a blank model to a new game state. Begin simulation."""
        print("Initializing Simulation...")

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

    # the two below are currently deprecated in favor of nation-level and object-level updates
    def on_monthly_update(self):
        """The monthly update loop for the game model."""
        for nation in self.nations:
            nation.on_monthly_update()

    def on_daily_update(self):
        """The daily update loop for the game model."""
        for nation in self.nations:
            nation.on_daily_update()

# --- Command Handling from Client --- Asyncio ---

    async def handle_client_command_deprecated(self, command_data: dict) -> dict:
        """Processes a command dictionary received from the Godot client."""
        
        command = command_data.get("command")
        
        # We need a reference to the player's Nation object for validation
        player_nation = self.player_nation 
        
        if not player_nation:
            return {"status": "ERROR", "response_to": command, "message": "Game not initialized."}

        # --- A critical first command for the client ---
        if command == "GET_INITIAL_STATE":
            # Godot client asks for the map data right after connecting.
            # You must return a fully serializable dictionary containing ALL
            # data needed for the client to draw the galaxy (star positions, hyperlanes, etc.)
            
            # NOTE: You will need a custom function to convert your Galaxy/Nation objects 
            # into simple Python dictionaries/lists for JSON to handle.
            return {
                "status": "OK",
                "response_to": "GET_INITIAL_STATE",
                "calendar": str(self.calendar),
                "galaxy_summary": f"Galaxy has {len(self.galaxy.solar_systems)} stars.",
                "player_name": player_nation.name,
                "player_resources": player_nation.resources # Assuming you add a resource attribute to Nation
            }
        
        # --- Example Player Action Command ---
        elif command == "BUILD_UNIT":
            unit_type = command_data.get("unit_type")
            system_id = command_data.get("location_id")
            
            # 1. Validation/Logic: Check if the player has resources, etc.
            # Example: cost = 100 
            # if player_nation.can_afford(cost):
            #     # 2. Authoritative State Change
            #     player_nation.deduct_resources(cost)
            #     self.galaxy.spawn_unit(unit_type, system_id, player_nation)
            
            return {
                "status": "OK",
                "response_to": "BUILD_UNIT",
                "log": f"Built command for {unit_type} received."
            }
            
        # --- Add all other player commands here (e.g., "MOVE_FLEET", "END_TURN") ---

        else:
            return {"status": "ERROR", "response_to": command, "message": f"Unknown command: {command}"}


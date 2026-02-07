import json
from commands import COMMAND_MAP

# --- Command handling and update sending ---
class ClientSession:
    """
    Per-client state and data management. Python representative of a specific connected client.
    Acts as a sort of profile for the connected player.
    Responsibilities include:
    - Tracking current view (galaxy, solar system, etc.)
    - Managing open menus and their data
    - Storing player-specific data (e.g., player ID)
    - Collects update data to send to the client
    """
    def __init__(self, game_world):
        self.game_world = game_world
        self.player_id = 1  # Placeholder, would be set upon login/authentication
        self.current_view = "GALAXY" # or "SOLAR_SYSTEM", etc.
        self.current_solar_system = None
        self.menus = [] # Dict of all menus, is_open = True/False

    #TODO: move on_update methods here, and have them simply return the packet for the invoker to cache and forward

class Invoker: 
    """
    AKA Command Router (or dispatcher).
    Responsibilities include:
    - Routing incoming commands to the appropriate command classes
    - Uses Client Session to validate commands (eg. permissions, current view)
    - Executing commands and returning responses
    - Broadcasting regular updates to clients
    """
    def __init__(self, game_model, client_session, server):
        self.game_model = game_model
        self.client_session = client_session
        self.server = server
        self.packet_cache = {}

    def receive_client_data(self, raw_message):
        try:
            packet = json.loads(raw_message)
            cmd_type = packet["type"]
            cmd_args = packet["args"]

            if cmd_type in COMMAND_MAP:
                command_class = COMMAND_MAP[cmd_type]
                instance = command_class(**cmd_args)
                instance.execute(self.game_model, self)  # Pass self as client session
            else:
                print(f"Error: Command '{cmd_type}' not recognized.")

        except TypeError as e:
            print(f"Error: Godot sent the wrong arguments for {cmd_type}: {e}")
        except Exception as e:
            print(f"General Error: {e}")

    def append_response(self, response_dict):
        self.packet_cache["data"]["response"] = response_dict
    
    # Separate Background Task
    async def prepare_response_packet(self):
        """Prepares responses to commands only. Called after each command is processed."""
        response_packet = {
            "type": "response",
            "timestamp": self.game_model.calendar.__str__(),
            "data": {}
        }
        if "response" in self.packet_cache.get("data", {}):
            response_packet["data"]["response"] = self.packet_cache["data"]["response"]
        
        # Clear the cache after preparing the response
        self.packet_cache = {}
        return json.dumps(response_packet) + '\n'  # Append newline for Godot


    def on_live_update(self):
        pass # Currently no live updates needed. Eventually will be needed for fleets.
        live_packet = {
            "type": "sync",
            "frequency": "live",
            "view": self.client_session.current_view,
            "timestamp": self.game_model.calendar.__str__(),
            "data": {}
        }

        if self.current_view == "GALAXY":
            live_packet["data"]["galaxy"] = self.live_galaxy()

        elif self.current_view == "SOLAR_SYSTEM":
            live_packet["data"]["solar_system"] = self.live_system()

        self.packet_cache = live_packet

    def on_daily_update(self):
        #import time, json
        #start = time.time()

        daily_packet = {
            "type": "sync",
            "frequency": "daily",
            "view": self.client_session.current_view,
            "timestamp": self.game_model.calendar.__str__(),
            "data": {}
        }

        if self.client_session.current_view == "GALAXY":
            daily_packet["data"]["galaxy"] = self.daily_galaxy()

        elif self.client_session.current_view == "SOLAR_SYSTEM":
            daily_packet["data"]["solar_system"] = self.daily_system()

        for menu in self.client_session.menus:
            if menu.is_open:
                daily_packet["data"][menu.name] = menu.get_data()

        self.packet_cache = daily_packet

        #json_str = json.dumps(self.packet_cache)
        #print("Serialization + assembly time took", time.time() - start, "seconds")
        #print("Live packet:", json.dumps(self.packet_cache, indent=2))  # Add this


    def on_monthly_update(self):
        pass

    # --- Data provider methods ---
    def galaxy_setup(self):
        return self.game_model.galaxy.setup_dict()
    
    def system_setup(self, system_id):
        system = self.game_model.get_system(system_id)
        return system.setup_dict()
    
    def live_galaxy(self):
        return self.game_model.galaxy.to_dict()
    
    def live_system(self):
        system = self.game_model.get_system(self.current_solar_system)
        return [system.to_dict()]
    
    def daily_galaxy(self):
        return self.game_model.galaxy.to_dict()

    def daily_system(self):
        system = self.game_model.get_system(self.current_solar_system)
        return system.to_dict()

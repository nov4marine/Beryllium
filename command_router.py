import json
from commands import COMMAND_MAP

class Invoker:
    def __init__(self):
        pass

    def on_start(self):
        pass

    def on_finish(self):
        print("Invoker finished processing commands.")
    
    def handle_client_data(raw_message, game_state):
        try:
            # Example JSON: {"type": "move_fleet", "args": {"fleet_id": 101, "x": 50, "y": -20}}
            packet = json.loads(raw_message)
            cmd_type = packet["type"]
            cmd_args = packet["args"]

            if cmd_type in COMMAND_MAP:
                # 1. Look up the class
                command_class = COMMAND_MAP[cmd_type]
                
                # 2. JSON Unpacking: Create the instance with the dictionary
                # This is where 'fleet_id', 'x', and 'y' are mapped automatically
                instance = command_class(**cmd_args)
                
                # 3. Execute
                instance.execute(game_state)
            else:
                print(f"Error: Command '{cmd_type}' not recognized.")

        except TypeError as e:
            print(f"Error: Godot sent the wrong arguments for {cmd_type}: {e}")
        except Exception as e:
            print(f"General Error: {e}")

    # TODO: implement command batching for efficiency later on

class ClientSession:
    def __init__(self):
        self.current_view = "GALAXY"  # Or a system_id like "SOL"
        self.open_menus = set()       # e.g., {"economy", "research"}

def broadcast_updates(game_state):
    for player_id, session in game_state.sessions.items():
        packet = {"type": "sync", "data": {}}
        
        # HIGH FREQUENCY: Ship positions in the current system
        if session.current_view != "GALAXY":
            system = game_state.get_system(session.current_view)
            packet["data"]["ships"] = system.get_ship_positions()
            
        # MEDIUM FREQUENCY: UI Data (only if menu is open)
        if "economy" in session.open_menus:
            packet["data"]["economy"] = game_state.get_economy_data(player_id)

        send_to_godot(player_id, packet)

    # TODO: implement flush system when views change
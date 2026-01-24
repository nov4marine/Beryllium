import json
from commands import COMMAND_MAP

class ClientSession:
    def __init__(self):
        self.current_view = "GALAXY"
        self.open_menus = set()

def handle_client_data(raw_message, game_state, session):
    try:
        packet = json.loads(raw_message)
        cmd_type = packet["type"]
        cmd_args = packet["args"]

        if cmd_type in COMMAND_MAP:
            command_class = COMMAND_MAP[cmd_type]
            instance = command_class(**cmd_args)
            instance.execute(game_state)
        else:
            print(f"Error: Command '{cmd_type}' not recognized.")

    except TypeError as e:
        print(f"Error: Godot sent the wrong arguments for {cmd_type}: {e}")
    except Exception as e:
        print(f"General Error: {e}")

async def send_update(writer, game_state, session):
    packet = {"type": "sync", "data": {}}

    # Example: Only send ships if not in galaxy view
    if session.current_view != "GALAXY":
        system = game_state.get_system(session.current_view)
        packet["data"]["ships"] = system.get_ship_positions()

    if "economy" in session.open_menus:
        packet["data"]["economy"] = game_state.get_economy_data("player1")

    writer.write((json.dumps(packet) + '\n').encode('utf-8'))
    await writer.drain()
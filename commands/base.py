# commands/base.py
COMMAND_MAP = {}

def register_command(name):
    def wrapper(cls):
        COMMAND_MAP[name] = cls
        return cls
    return wrapper

from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self, game_model, client_id):
        """Now every command knows who called it."""
        pass

# Possibly later add validation, logging, etc.
# Command validation includes:
# 1. Ownership checks (is the player allowed to do this?)
# 2. Resource checks (does the player have enough resources?)
# 3. Legality checks (is the action allowed by game rules? Is it outside cooldowns or game world?)

# Example command validation:
# Inside your MoveFleet command
def execute(self, game_model, player_session):
    fleet = game_model.get_fleet(self.fleet_id)
    
    # VALIDATION
    if fleet.owner_id != player_session.player_id:
        return False, "You do not own this fleet."
    
    if not game_model.is_path_clear(fleet.pos, self.target):
        return False, "Path is blocked."

    # EXECUTION (Only reached if valid)
    fleet.move_to(self.target)
    return True, "Success"


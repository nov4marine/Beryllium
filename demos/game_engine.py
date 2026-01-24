import asyncio
import time
import json

class GameEngine:
    def __init__(self):
        # Initialize your core simulation state here
        self.current_turn = 1
        self.resources = {"Player_1": 100, "Player_2": 100}
        self.units = []
        self.is_processing_turn = False
        
        print("🌍 Game Engine initialized.")

    async def process_client_command(self, client_id, command_data):
        """Processes an instant command (like building a unit or moving a fleet)."""
        
        command_type = command_data.get("command")
        
        # 1. Start Validation & Simulation
        print(f"Engine processing command: {command_type} from Client {client_id}")

        # Check if the command is valid given the current game state
        if command_type == "BUILD_UNIT":
            unit_type = command_data.get("unit_type")
            cost = 50 # Example cost
            
            if self.resources["Player_1"] >= cost:
                # 2. Update the authoritative state
                self.resources["Player_1"] -= cost
                new_unit_id = len(self.units) + 1
                self.units.append({"id": new_unit_id, "type": unit_type, "location": command_data.get("location_id")})
                
                # 3. Generate a response for the client
                response = {
                    "status": "OK",
                    "response_to": "BUILD_UNIT",
                    "unit_id": new_unit_id,
                    "new_resources": self.resources["Player_1"]
                }
            else:
                response = {
                    "status": "ERROR",
                    "response_to": "BUILD_UNIT",
                    "message": "Insufficient resources."
                }
        
        elif command_type == "END_TURN":
            # For turn-based grand strategy, this triggers the most complex calculations
            response = await self.run_turn_simulation()
            
        else:
            response = {"status": "ERROR", "message": f"Unknown command: {command_type}"}

        # Crucial: Always return a response dictionary
        return response

    async def run_turn_simulation(self):
        """Simulates all turn-based changes (resource collection, combat, growth)."""
        if self.is_processing_turn:
            return {"status": "ERROR", "message": "Turn already processing."}
            
        self.is_processing_turn = True
        print(f"\n⚙️ Starting Turn {self.current_turn} simulation...")
        
        # Simulate a time-consuming step without blocking the network (using await asyncio.sleep)
        await asyncio.sleep(0.1) # Simulate complex math/AI for 100ms
        
        # Update state for the next turn
        self.current_turn += 1
        self.resources["Player_1"] += 20
        self.resources["Player_2"] += 15
        
        self.is_processing_turn = False
        print(f"✅ Turn {self.current_turn - 1} complete.")
        
        # Generate the broadcast update (The client needs the full new state)
        return {
            "status": "UPDATE",
            "update_type": "END_OF_TURN_STATE",
            "turn": self.current_turn,
            "resources": self.resources
        }
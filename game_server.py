import asyncio
import json
import time

# Assuming your files are organized so you can import them:
# If model.py is NOT inside a package, use: from model import GameWorld
# Otherwise:
from model.model import GameWorld 

HOST = '127.0.0.1'
PORT = 8888

# 🚨 The Authoritative Game Model 
# This single instance holds the entire state (Galaxy, Nations, Calendar)
game_model = GameWorld()

# --- Async Task to Run the Game Clock ---

async def game_clock_task():
    """
    Asynchronous task to run the game's calendar and simulation ticks.
    This replaces the synchronous 'update(delta_time)' loop.
    """
    
    # 1. Initialize the Game World (Galaxy generation, Nation deployment, etc.)
    # This runs the synchronous setup methods you wrote (Galaxy.__init__ etc.)
    print("⏳ Initializing Game World (Galaxy, Nations, etc.)...")
    # This calls GameWorld.initialize_new_game() which runs your setup
    game_model.initialize_new_game()
    print("✅ Initialization complete. Simulation ready.")
    
    # 2. Run the continuous simulation loop
    # Based on your calendar.py, time_per_game_day is 1 second, so we tick every second.
    while True:
        if game_model.galaxy: 
            # Call your existing synchronous advance_day method
            # This triggers all daily/monthly observers (Galaxy, Nations)
            game_model.calendar.advance_day()
            
            # TODO: Implement a system to broadcast STATE DELTAS to the client here
            current_date = game_model.calendar.__str__()
            print(f"[{current_date}] ⚙️ Day Advanced.")
            
        # CRITICAL: Use await asyncio.sleep() to pause the task without blocking
        # the entire server's event loop (which is handling network I/O).
        await asyncio.sleep(game_model.calendar.time_per_game_day) 
        # Sleep for 1 second (or whatever your game day duration is)

# --- Client Command Handling ---

async def handle_client_connection(reader, writer):
    """Handles an individual client connection and command processing."""
    addr = writer.get_extra_info('peername')
    print(f"Client connected from {addr}")
    
    try:
        while True:
            # READ: Waits for a full message ending in newline (required by Godot)
            data = await reader.readuntil(b'\n')
            message = data.decode('utf-8').strip()
            
            try:
                game_command = json.loads(message)
                print(f"⬅️  Received command from {addr}: {game_command.get('command')}")
                
                # 2. Process Command (Delegate to a GameWorld method for logic)
                # NOTE: This method must be added to your GameWorld class (see below)
                server_response = await game_model.handle_client_command(game_command)
                
            except json.JSONDecodeError:
                server_response = {"status": "ERROR", "message": "Invalid JSON format received."}
            
            except Exception as e:
                server_response = {"status": "ERROR", "message": f"Server processing error: {e}"}

            # 3. Send Response
            print(f"➡️  Sending response to {addr}: {server_response.get('status')}")
            response_json = json.dumps(server_response) + '\n'
            writer.write(response_json.encode('utf-8'))
            await writer.drain()

    except asyncio.IncompleteReadError:
        print(f"Closing connection to {addr} (Incomplete Read)")
    except ConnectionResetError:
        print(f"Client {addr} forcefully disconnected.")
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Connection closed for {addr}")


# --- Main Server Initialization ---

async def main():
    # Start the TCP server, routing new connections to the handler
    server = await asyncio.start_server(
        handle_client_connection, 
        HOST, PORT
    )
    addr = server.sockets[0].getsockname()
    print(f"Python Server: Serving on {addr}")
    
    # Start the game clock task concurrently with the network server
    # This is how the simulation runs independently of client connections
    asyncio.create_task(game_clock_task())
    
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutting down.")
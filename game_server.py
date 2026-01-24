import asyncio
import json
import time

# Assuming your files are organized so you can import them:
# If model.py is NOT inside a package, use: from model import GameWorld
# Otherwise:
from model.model import GameModel
from command_router import *

HOST = '127.0.0.1'
PORT = 8888

# 🚨 The Authoritative Game Model 
# This single instance holds the entire state (Galaxy, Nations, Calendar)
game_model = GameModel()

client_session = None  # Placeholder for client session management
client_writer = None  # Placeholder for client writer stream

# --- Async Task to Run the Game Clock ---

async def game_clock_task():
    """
    Asynchronous task to run the game's calendar for simulation ticks.
    """
    global client_writer, client_session
    # 1. Initialize the Game World (Galaxy generation, Nation deployment, etc.)
    # This runs the synchronous setup methods you wrote (Galaxy.__init__ etc.)
    print("⏳ Initializing Game World (Galaxy, Nations, etc.)...")
    # This calls GameWorld.initialize_new_game() which runs your setup. 
    game_model.initialize_new_game()
    print("✅ Initialization complete. Simulation ready.")
    
    # 2. Run the continuous simulation loop
    # Based on your calendar.py, time_per_game_day is 1 second, so we tick every second.
    while True:
        if game_model.galaxy: 
            # Call your existing synchronous advance_day method
            # This triggers all daily/monthly observers (Galaxy, Nations)
            game_model.calendar.advance_day()
            
            current_date = game_model.calendar.__str__()
            print(f"[{current_date}] ⚙️ Day Advanced.")

            # 3. After advancing the day, send updates to connected clients
            if client_writer and client_session:
                await send_update(client_writer, game_model, client_session)
            
        # CRITICAL: Use await asyncio.sleep() to pause the task without blocking
        # the entire server's event loop (which is handling network I/O).
        await asyncio.sleep(game_model.calendar.time_per_game_day) 
        # Sleep for 1 second (or whatever your game day duration is)
        # TODO: adjust later such that each tick represents the smallest calendar step

# --- Client Command Handling ---

async def handle_client_connection(reader, writer):
    """Handles an individual client connection and command processing."""
    global client_writer, client_session
    addr = writer.get_extra_info('peername')
    print(f"Client connected from {addr}")

    # Create a session for this client
    client_session = ClientSession()
    client_writer = writer
    
    try:
        while True:
            # READ: Waits for a full message ending in newline (required by Godot)
            data = await reader.readuntil(b'\n')
            message = data.decode('utf-8').strip()
            
            # Handle the command
            handle_client_data(message, game_model, client_session)

            # Send Response
            await send_update(writer, game_model, client_session)

    except asyncio.IncompleteReadError:
        print(f"Closing connection to {addr} (Incomplete Read)")
    except ConnectionResetError:
        print(f"Client {addr} forcefully disconnected.")
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Connection closed for {addr}")
        client_writer = None
        client_session = None

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
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

client_session = ClientSession(game_model)  # Placeholder for client session management
client_writer = None  # Placeholder for client writer stream
game_model.calendar.add_daily_observer(client_session)

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
        tick_start = time.time()
        if game_model.galaxy: 
            # Call your existing synchronous advance_day method
            # This triggers all daily/monthly observers (Galaxy, Nations)
            game_model.calendar.update()
            
            # 3. After advancing the day, send updates to connected clients
            if client_writer and client_session:
                print(f"packet cache: {client_session.packet_cache}")  # Debug: Show the packet before sending
                await client_session.send_update(client_writer)
            #print("✅ Clients updated.")

        tick_duration = time.time() - tick_start
        if tick_duration > 1.0:
            print(f"⏱️ Tick Duration: {tick_duration:.3f} seconds")
            
        # CRITICAL: Use await asyncio.sleep() to pause the task without blocking
        # the entire server's event loop (which is handling network I/O).
        await asyncio.sleep(game_model.calendar.time_per_tick) 
        # Sleep for 1 second (or whatever your game day duration is)
        # TODO: adjust later such that each tick represents the smallest calendar step

# --- Client Command Handling ---

async def handle_client_connection(reader, writer):
    """Handles an individual client connection and command processing."""
    global client_writer, client_session
    addr = writer.get_extra_info('peername')
    print(f"Client connected from {addr}")

    # Create a session for this client
    client_writer = writer

    print(f"client_writer: {client_writer}, client_session: {client_session}")

    
    try:
        while True:
            # READ: Waits for a full message ending in newline (required by Godot)
            data = await reader.readuntil(b'\n')
            message = data.decode('utf-8').strip()
            
            # Handle the command
            client_session.handle_client_data(message)

            # Send Response
            await client_session.send_update(writer)

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

# --- Major Refactor of the above code --- #
# 3 coponents: Server (handles the direct socket communication, (reading and writing)),

class Server:
    """
    Handles the direct socket communication, reading and writing.
    """
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port

        self.writer = None  # Will be set upon client connection
        self.reader = None  # Will be set upon client connection

        self.game_model = None  # Will be set by another method 
        self.command_invoker = None
        self.client_session = None

    async def start(self):
        """Starts the TCP server and listens for client connections."""
        server = await asyncio.start_server(
            self.handle_client_connection, 
            self.host, self.port
        )
        addr = server.sockets[0].getsockname()
        print(f"Python Server: Serving on {addr}")
        
        async with server:
            await server.serve_forever()

    def start_new_game(self):
        """Initializes the authoritative game model."""
        self.game_model = GameModel()
        self.game_model.initialize_new_game()
        self.client_session = ClientSession(self.game_model)
        self.command_invoker = Invoker(self.game_model, self.client_session, self)
        # Add more setup as needed.

    async def handle_client_connection(self, reader, writer):
        """Handles an individual client connection and command processing."""
        addr = writer.get_extra_info('peername')
        print(f"Client connected from {addr}")
        self.writer = writer
        self.game_model.calendar.add_daily_observer(client_session)

        try:
            while True:
                # READ: Waits for a full message ending in newline (required by Godot)
                data = await reader.readuntil(b'\n')
                message = data.decode('utf-8').strip()
                
                # Receive the command
                self.command_invoker.receive_client_data(message)

                # Send Data Response
                response = self.command_invoker.prepare_response_packet()

                writer.write((json.dumps(response) + '\n').encode('utf-8'))
                await writer.drain()

        except asyncio.IncompleteReadError:
            print(f"Closing connection to {addr} (Incomplete Read)")
        except ConnectionResetError:
            print(f"Client {addr} forcefully disconnected.")
        finally:
            writer.close()
            await writer.wait_closed()
            print(f"Connection closed for {addr}")
            self.game_model.calendar.remove_daily_observer(client_session)

###
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

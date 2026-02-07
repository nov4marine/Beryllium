import asyncio
import json
import time
from model.model import GameModel
from command_router import *

class Server:
    """
    Handles the direct socket communication, reading and writing.
    """
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.writer = None
        self.reader = None
        self.game_model = None
        self.command_invoker = None
        self.client_session = None
        self.is_game_running = False

    async def start(self):
        self.start_new_game()
        server = await asyncio.start_server(self.handle_client_connection, self.host, self.port)
        print(f"Python Server: Serving on {self.host}:{self.port}")
        asyncio.create_task(self.game_clock_task())
        async with server:
            await server.serve_forever()

    def start_new_game(self):
        """Initializes the authoritative game model."""
        self.game_model = GameModel()
        self.game_model.initialize_new_game()
        self.client_session = ClientSession(self.game_model)
        self.command_invoker = Invoker(self.game_model, self.client_session, self)
        self.game_model.calendar.add_daily_observer(self.command_invoker)
        self.is_game_running = True
        # Add more setup as needed.

    async def handle_client_connection(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Client connected from {addr}")
        self.writer = writer
        self.reader = reader
        try:
            while True:
                # READ: Waits for a full message ending in newline (required by Godot)
                data = await reader.readuntil(b'\n')
                message = data.decode('utf-8').strip()
                self.command_invoker.receive_client_data(message)
                response = self.command_invoker.prepare_response_packet()
                await self.send_packet(response)
        except asyncio.IncompleteReadError:
            print(f"Closing connection to {addr} (Incomplete Read)")
        except ConnectionResetError:
            print(f"Client {addr} forcefully disconnected.")
        finally:
            writer.close()
            await writer.wait_closed()
            print(f"Connection closed for {addr}")
            self.game_model.calendar.remove_daily_observer(self.command_invoker)

    async def send_packet(self, packet):
        if self.writer:
            self.writer.write((json.dumps(packet) + '\n').encode('utf-8'))
            await self.writer.drain()

    async def game_clock_task(self):
        """
        Asynchronous task to run the game's calendar for simulation ticks.
        """
        # 2. Run the continuous simulation loop
        # Based on your calendar.py, time_per_game_day is 1 second, so we tick every second.
        while True:
            tick_start = time.time()
            if self.is_game_running and self.game_model.galaxy:
                self.game_model.calendar.update()
                # Send update to client if connected
                if self.client_session and self.writer:
                    await self.client_session.send_update(self.writer)
            tick_duration = time.time() - tick_start
            if tick_duration > 1.0:
                print(f"⏱️ Tick Duration: {tick_duration:.3f} seconds")
            await asyncio.sleep(self.game_model.calendar.time_per_tick)

if __name__ == '__main__':
    try:
        server = Server()
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nServer shutting down.")


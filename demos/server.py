import asyncio
import json

# --- Configuration ---
HOST = '127.0.0.1'  # 'localhost' - The IP address the server will listen on.
PORT = 8888         # The port number to use for communication.

# A simple list to keep track of all connected clients (for later broadcast)
clients = []

async def handle_client(reader, writer):
    """
    This coroutine is executed for every new client connection.
    It reads messages, processes them, and sends a response.
    """
    addr = writer.get_extra_info('peername')
    print(f"🎉 Client connected from {addr}")

    # Add the client writer to our list
    clients.append(writer)

    try:
        while True:
            # 1. Read data from the client
            # The client should ensure a complete, single message is sent.
            # We'll read up to a certain size. You will need logic here to
            # handle message boundaries if messages are large.
            data = await reader.readuntil(b'\n')  # Read until newline character
            
            if not data:
                # Connection closed by client
                break

            # 2. Decode bytes to string
            message = data.decode('utf-8').strip() # strip to remove newline delimiter

            # 3. Deserialize the JSON message
            try:
                # Assuming the client sends a complete JSON string
                game_command = json.loads(message)
                print(f"⬅️  Received command: {game_command}")

                # --- Game Logic / Simulation Hook ---
                # This is where your Python simulation model gets its input.
                # For now, let's just create a simple JSON response.
                response_data = {
                    "status": "ok",
                    "response_to": game_command.get("command", "N/A"),
                    "turn": 1,
                    "message": "Command received and processed!"
                }
                # ------------------------------------

            except json.JSONDecodeError:
                print(f"⚠️  Received non-JSON data: {message}")
                response_data = {"status": "error", "message": "Invalid JSON format"}


            # 4. Serialize the response back to JSON string
            response_json = json.dumps(response_data)
            
            # Critical Fix: add a newline delimiter to indicate end of message
            response_json += '\n'

            # 5. Encode the string back to bytes and send
            writer.write(response_json.encode('utf-8'))
            await writer.drain() # Wait until the buffer is flushed

    except ConnectionResetError:
        # Client forcibly closed the connection
        print(f"💀 Client {addr} forcibly disconnected.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Clean up the connection
        print(f"👋 Closing connection to {addr}")
        clients.remove(writer)
        writer.close()

async def main():
    """
    The main server function that starts listening.
    """
    server = await asyncio.start_server(
        handle_client, HOST, PORT)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f"✨ Python Server: Serving on {addrs}")

    async with server:
        # Run the server forever, accepting connections and tasks
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user.")
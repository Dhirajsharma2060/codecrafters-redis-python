import socket
import threading
import time
import argparse

key_value_store = {}
expiry_times = {}
lock = threading.Lock()

def handle_ping(parts, client_socket):
    response = "+PONG\r\n"
    client_socket.send(response.encode())

def handle_echo(parts, client_socket):
    message = parts[4]
    response = f"${len(message)}\r\n{message}\r\n"
    client_socket.send(response.encode())

def handle_set(parts, client_socket):
    key = parts[4]
    value = parts[6]
    with lock:
        key_value_store[key] = value
    response = "+OK\r\n"
    client_socket.send(response.encode())

def handle_get(parts, client_socket):
    key = parts[4]
    with lock:
        if key in key_value_store and (key not in expiry_times or time.time() < expiry_times[key]):
            value = key_value_store[key]
            response = f"${len(value)}\r\n{value}\r\n"
        else:
            response = "$-1\r\n"  # Key not found or expired
    client_socket.send(response.encode())

def handle_set_px(parts, client_socket):
    key = parts[4]
    value = parts[6]
    expiry_time_ms = int(parts[10])
    with lock:
        key_value_store[key] = value
        expiry_times[key] = time.time() + expiry_time_ms / 1000.0
    response = "+OK\r\n"
    client_socket.send(response.encode())

command_handlers = {
    "PING": handle_ping,
    "ECHO": handle_echo,
    "SET": handle_set,
    "GET": handle_get,
}

def handle_client(client_socket, client_address):
    print(f"Client: {client_address}")
    try:
        while True:
            request = client_socket.recv(1024)
            if not request:
                break  # if no more data, then the connection will break
            
            data = request.decode()
            print(f"Received data: {data}")
            
            parts = data.split("\r\n")
            print(f"Parsed parts: {parts}")  # Log the parsed parts
            
            try:
                if parts[0] == "*1" and parts[2].upper() in command_handlers:
                    command_handlers[parts[2].upper()](parts, client_socket)
                elif parts[0] == "*5" and parts[2].upper() == "SET" and parts[8].upper() == "PX":
                    handle_set_px(parts, client_socket)
                else:
                    response = "-ERROR\r\n"
                    client_socket.send(response.encode())
            except IndexError as e:
                print(f"IndexError: {e}")
                response = "-ERROR\r\n"
                client_socket.send(response.encode())
            except Exception as e:
                print(f"Unexpected error: {e}")
                response = "-ERROR\r\n"
                client_socket.send(response.encode())
    
    except Exception as ex:
        print(f"Error handling the client {client_address}: {ex}")
    finally:
        client_socket.close()
        print(f"Client {client_address} is disconnected")

def main():
    parser = argparse.ArgumentParser(description='Start a Redis-like server.')
    parser.add_argument('--port', type=int, default=6379, help='Port number to run the server on')
    args = parser.parse_args()

    print(f"Starting server on port {args.port}")
    server_socket = socket.create_server(("localhost", args.port), reuse_port=True)

    while True:
        client_socket, address = server_socket.accept()  # Accept client connection
        print(f"Accepted connection from {address[0]}:{address[1]}")
        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        # Start a thread for each new client
        client_thread.start()

if __name__ == "__main__":
    main()

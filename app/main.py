import socket
import threading
import time

key_value_store = {}
expiry_times = {}

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
            
            if parts[0] == "*1" and parts[2].upper() == "PING":  # Check correct structure
                response = "+PONG\r\n"
                client_socket.send(response.encode())
            elif parts[0] == "*2" and parts[2].upper() == "ECHO":
                message = parts[4]
                response = f"${len(message)}\r\n{message}\r\n"
                client_socket.send(response.encode())
            elif parts[0] == "*3" and parts[2].upper() == "SET":
                key = parts[4]
                value = parts[6]
                key_value_store[key] = value  # Store key-value pair in the dictionary
                response = "+OK\r\n"
                client_socket.send(response.encode())
            elif parts[0] == "*2" and parts[2].upper() == "GET":
                key = parts[4]
                if key in key_value_store and (key not in expiry_times or time.time() < expiry_times[key]):
                    value = key_value_store[key]
                    response = f"${len(value)}\r\n{value}\r\n"
                else:
                    response = "$-1\r\n"  # Key not found or expired response
                client_socket.send(response.encode())
            elif parts[0] == "*5" and parts[2].upper() == "SET" and parts[8].upper() == "PX":
                key = parts[4]
                value = parts[6]
                expiry_time_ms = int(parts[10])
                key_value_store[key] = value  # Store key-value pair in the dictionary
                expiry_times[key] = time.time() + expiry_time_ms / 1000.0  # Set expiry time in seconds
                response = "+OK\r\n"
                client_socket.send(response.encode())
            else:
                # Handle unexpected input or commands
                response = "-ERROR\r\n"
                client_socket.send(response.encode())
    
    except Exception as ex:
        print(f"Error handling the client {client_address}: {ex}")
    finally:
        client_socket.close()
        print(f"Client {client_address} is disconnected")

def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        client_socket, address = server_socket.accept()  # Accept client connection
        print(f"Accepted connection from {address[0]}:{address[1]}")
        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        # Start a thread for each new client
        client_thread.start()

if __name__ == "__main__":
    main()

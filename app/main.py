import socket
import threading

def handle_client(client_socket, client_address):
    print(f"Client: {client_address}")
    try:
        while True:
            request = client_socket.recv(1024)
            if not request:
                break  # if no more data, then the connection will break
            
            data = request.decode()
            
            if data.startswith("*1") and "PING" in data:
                response = "+PONG\r\n"
                client_socket.send(response.encode())
            elif data.startswith("*2") and "ECHO" in data:
                parts = data.split("\r\n")
                message = parts[4]
                response = f"${len(message)}\r\n{message}\r\n"
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

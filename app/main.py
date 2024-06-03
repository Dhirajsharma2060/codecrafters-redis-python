import socket
import threading

def handle_client(client_address, client_socket):
    print(f"Client: {client_address}")
    try:
        while True:
            request = client_socket.recv(512)
            if not request:
                break  # if no more data, then the connection will break

            # Split the request into commands by CRLF (\r\n)
            commands = request.decode().split('\r\n')
            for command in commands:
                if command == '':
                    continue  # Skip empty commands

                parts = command.split()
                if not parts:
                    continue

                cmd = parts[0].lower()

                if cmd == "ping":
                    client_socket.sendall(b"+PONG\r\n")
                elif cmd == "echo" and len(parts) > 1:
                    message = " ".join(parts[1:])
                    response = f"${len(message)}\r\n{message}\r\n"
                    client_socket.sendall(response.encode())
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
        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(address, client_socket))
        # Start a thread for each new client
        client_thread.start()

if __name__ == "__main__":
    main()

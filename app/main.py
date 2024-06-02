import socket

def main():
    print("Logs from your program will appear here!")

    pong_response = "+PONG\r\n"
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    
    while True:
        client_socket, address = server_socket.accept()  # Accept client connection
        print(f"Client connected: {address}")

        try:
            while True:
                request = client_socket.recv(512)  # Receive request from client
                if not request:
                    break  # Break if no more data

                # Split the request by CRLF (\r\n) to handle multiple commands
                commands = request.decode().split('\r\n')
                for command in commands:
                    if command.lower() == "ping":
                        client_socket.sendall(pong_response.encode())  # Send "+PONG\r\n" response
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()  # Close client socket after handling request

if __name__ == "__main__":
    main()

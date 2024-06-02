# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    pong="+PONG\r\n"
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    #server_socket.accept() # wait for client
    client=server_socket.accept()#client socket ke through accept karega 
    #client.send(pong.encode())
    while True:#always true 
        request: bytes = client.recv(512)#request jho bhi ho 
        data: str = request.decode()#request ka data decode hoga 
        # print(data)
        if "ping" in data.lower():#agar ping hai to client ko PONg 
            client.send(pong.encode())



if __name__ == "__main__":
    main()

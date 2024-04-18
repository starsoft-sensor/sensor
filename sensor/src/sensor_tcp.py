import socket

# Define the host and port to listen on
HOST = 'localhost'
PORT = 12345

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen(5)
print(f"TCP server is listening on {HOST}:{PORT}")

while True:
    # Accept incoming connection
    client_socket, client_address = server_socket.accept()
    print(f"Connected to client: {client_address}")

    try:
        # Receive data from the client
        data = client_socket.recv(4096)
        if data:
            print(f"Received data from client: {data.decode()}")

            # Process the received data (e.g., perform some operations)

            # Send a response back to the client
            response = b"Hello from TCP server!"
            client_socket.sendall(response)
            print("Response sent to client")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the client socket
        client_socket.close()
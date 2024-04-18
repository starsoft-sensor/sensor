import socket

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 12345)
server_socket.bind(server_address)

print('UDP server is listening')

# Receive and print data
while True:
    data, address = server_socket.recvfrom(4096)
    print('Received:', data.decode(), 'from', address)

    # Echo back the data
    server_socket.sendto(data, address)
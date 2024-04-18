import socket
import argparse
import os, glob
import sys

def main(run_py_file):
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="波形データ")
    args = parser.parse_args()
    data = args.data
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Define the server address and port
    server_address = ('133.18.23.48', 12345)

    # Send data
    message = data.encode('utf-8')
    client_socket.sendto(message, server_address)

    # Receive response
    # data, server = client_socket.recvfrom(4096)
    # print('Received:', data.decode())

    # Close the socket
    client_socket.close()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    main(__file__)
    sys.exit(0)
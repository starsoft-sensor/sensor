import socket
import argparse
import os, glob
import sys

# Define the server's host and port
HOST = 'localhost'
PORT = 12345

def main(run_py_file):
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="波形データ")
    args = parser.parse_args()
    data = args.data
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        client_socket.connect((HOST, PORT))
        print(f"Connected to server: {HOST}:{PORT}")

        # Send data to the server
        message = data
        client_socket.sendall(message.encode())
        print(f"Sent data to server: {message}")

        # Receive response from the server
        response = client_socket.recv(4096)
        if response:
            print(f"Received response from server: {response.decode()}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the client socket
        client_socket.close()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    main(__file__)
    sys.exit(0)

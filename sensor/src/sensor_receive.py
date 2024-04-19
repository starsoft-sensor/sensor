import argparse
from datetime import datetime
import sys
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import japanize_matplotlib
import socket
import db_common as db

HOST = '133.18.23.48'
PORT = 12345
graph_dir = '../graph'

wave_data_list = []
db_conn = None
db_cur = None
def compare_waveforms(waveform1, waveform2):
    # RMSE
    rmse = np.sqrt(np.mean((waveform1 - waveform2) ** 2))

    # Corr
    corr_coef = np.corrcoef(waveform1, waveform2)[0, 1]

    # Cross-correlation
    xcorr = signal.correlate(waveform1, waveform2, mode='full')

    # Cross-correlation Peak
    peak_index = np.argmax(xcorr)
    peak_value = xcorr[peak_index]

    return rmse, corr_coef, peak_index, peak_value

def find_time_delay(waveform1, waveform2):
    # Cross-correlation
    xcorr = signal.correlate(waveform1, waveform2, mode='full')

    # Cross-correlation max peak offset
    time_delay = np.argmax(xcorr) - (len(waveform1) - 1)

    return time_delay

def adjust_phase(waveform1, waveform2, time_delay):
    # time_delay<0 waveform2 precedes waveform1, make waveform2 right.
    # time_delay>0 waveform2 follows waveform1, make waveform2 left.
    if time_delay < 0:
        adjusted_waveform2 = np.roll(waveform2, -time_delay)
    elif time_delay > 0:
        adjusted_waveform2 = np.roll(waveform2, len(waveform2) - time_delay)
    else:
        adjusted_waveform2 = waveform2

    return adjusted_waveform2

def check_similarity(waveform1, waveform2):
    # Check if two waveforms same.
    return np.array_equal(waveform1, waveform2)

def draw_same(waveform1, waveform2):
    x = []
    for i in range(len(waveform1)):
        x.append(i)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))

    ax[0].plot(x, waveform1, marker='o', color='b', linestyle='-')
    ax[0].set_title('波形表示 WaveForm1')
    ax[0].set_xlabel('X')
    ax[0].set_ylabel('Y')
    ax[1].plot(x, waveform2, marker='s', color='r', linestyle='--')
    ax[1].set_title('波形表示 WaveForm2')
    ax[1].set_xlabel('X')
    ax[1].set_ylabel('Y')

    plt.tight_layout()

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    filename = graph_dir + '/' + str(timestamp) + '.png'
    plt.savefig(filename)

def draw_diff(waveform1, waveform2):
    x = []
    for i in range(len(waveform1)):
        x.append(i)
    plt.figure(figsize=(8, 6))
    plt.plot(x, waveform1, marker='o', color='b', linestyle='-', label='waveform1')
    plt.plot(x, waveform2, marker='s', color='r', linestyle='--', label='waveform2')
    plt.legend()
    plt.title('波形表示')
    plt.xlabel('X')
    plt.ylabel('Y')

    plt.grid(True)

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    filename =  graph_dir + '/' + str(timestamp) + '.png'
    plt.savefig(filename)
def start_process(waveform1, waveform2):
    rmse, corr_coef, peak_index, peak_value = compare_waveforms(waveform1, waveform2)
    # Fimd time dealy of two waveforms
    if len(waveform1 < waveform2):
        waveform2[0:len(waveform1)]
    else:
        waveform1[0:len(waveform2)]
    time_delay = find_time_delay(waveform1, waveform2)

    # Adjust wavefrom2 relative to waveform1
    adjusted_waveform2 = adjust_phase(waveform1, waveform2, len(waveform2) - time_delay)

    # Check if two waveforms same.
    is_similar = check_similarity(waveform1, adjusted_waveform2)
    print(is_similar)
    if is_similar == True:
        draw_same(waveform1, waveform2)
    else:
        draw_diff(waveform1, waveform2)

def connect_db(db_server, db_user, db_pass, sid, ssh_server, ssh_user, ssh_pass):
    print('connect_db...')
    server = None
    if ssh_server != '':
        server = db.connect_ssh(ssh_server, ssh_user, ssh_pass, db_server)
    global db_conn
    db_conn, db_cur = db.connect_mysql_db(server, db_server, db_user, db_pass, sid)
    # db.connect_mysql(ssh_server, 22, ssh_user, ssh_pass, db_server, 3306, db_user,
    #                   db_pass, sid)
    print(db_conn)
    return db_conn, db_cur

def insert_db(timestamp, data):
    try:
        with db_conn.cursor() as cursor:
            sql = "INSERT INTO sensor_data (collect_time, collected_data) VALUES (%s, %s)"
            cursor.execute(sql, (timestamp, data))
        db_conn.commit()
    except Exception as e:
        db_conn.rollback()
        print("Error:", e)

def net_start(network):
    if network == 'udp':
        udp_start()
    elif network == 'tcp':
        tcp_start()

def udp_start():
    print(db_conn)
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = (HOST, PORT)
    server_socket.bind(server_address)

    print('UDP server is listening')

    # Receive and print data
    while True:
        data, address = server_socket.recvfrom(4096)
        print('Received:', data.decode(), 'from', address)
        wave_data_list.append(data.decode())
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        insert_db(timestamp, data.decode())
        if len(wave_data_list) >= 2:
            data1 = wave_data_list[-1]
            data2 = wave_data_list[-2]
            waveform1 = np.array([int(x) for x in data1.split(',')])
            waveform2 = np.array([int(x) for x in data2.split(',')])
            start_process(waveform1, waveform2)

def tcp_start():
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
                wave_data_list.append(data.decode())
                if len(wave_data_list) >= 2:
                    data1 = wave_data_list[-1]
                    data2 = wave_data_list[-2]
                    waveform1 = np.array([int(x) for x in data1.split(',')])
                    waveform2 = np.array([int(x) for x in data2.split(',')])
                    start_process(waveform1, waveform2)
                # Send a response back to the client
                response = b"Hello from TCP server!"
                client_socket.sendall(response)
                print("Response sent to client")

        except Exception as e:
            print(f"Error: {e}")

        finally:
            # Close the client socket
            client_socket.close()
def main(run_py_file):
    parser = argparse.ArgumentParser()
    # parser.add_argument("--data1", type=str, required=True, help="波形データ1")
    # parser.add_argument("--data2", type=str, required=True, help="波形データ2")
    parser.add_argument("--network", type=str, required=True, help="tcp, udp")
    parser.add_argument('--db_server', type=str, required=True, help="DB サーバアドレス")
    parser.add_argument('--db_user', type=str, required=True, help="DB User Name")
    parser.add_argument('--db_pass', type=str, required=True, help="DB Password")
    parser.add_argument('--sid', type=str, required=True, help='sid')
    parser.add_argument('--ssh_server', type=str, default='', help="ssh サーバアドレス")
    parser.add_argument('--ssh_user', type=str, default='', help="ssh User Name")
    parser.add_argument('--ssh_pass', type=str, default='', help="ssh Password")

    args = parser.parse_args()
    # data1 = args.data1
    # data2 = args.data2
    network = args.network
    db_server = args.db_server
    db_user = args.db_user
    db_pass = args.db_pass
    sid = args.sid
    ssh_server = args.ssh_server
    ssh_user = args.ssh_user
    ssh_pass = args.ssh_pass

    print("Starting...")
    # waveform1 = np.array([int(x) for x in data1.split(',')])
    # waveform2 = np.array([int(x) for x in data2.split(',')])

    db_conn, db_cur = connect_db(db_server, db_user, db_pass, sid, ssh_server, ssh_user, ssh_pass)
    net_start(network)

    # start_process(waveform1, waveform2)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    main(__file__)
    sys.exit(0)

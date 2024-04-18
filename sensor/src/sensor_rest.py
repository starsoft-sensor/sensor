from flask import Flask, request, jsonify, send_file
import db_common as db
import argparse
from datetime import datetime
import sys
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import io
import japanize_matplotlib

db_conn = None
db_cur = None
graph_dir = '../graph'

app = Flask(__name__)


@app.route('/sensor', methods=['GET'])
def get_all_sensor():
    with db_conn.cursor() as cursor:
        sql = f"SELECT collect_time, collected_data from sensor_data"
        cursor.execute(sql)
        rows = cursor.fetchall()
        data_list = []
        for row in rows:
            timestamp = row[0]
            data = row[1]
            data_list.append({'timestamp': timestamp, 'data': data})

    return jsonify(data_list)

@app.route('/sensor/<timestamp>', methods=['GET'])
def get_sensor(timestamp):
    db_conn.ping(reconnect=True)
    with db_conn.cursor() as cursor:
        sql = f"SELECT collect_time, collected_data from sensor_data WHERE collect_time={timestamp}"
        cursor.execute(sql)
        rows = cursor.fetchall()
        data_list = []
        for row in rows:
            timestamp = row[0]
            data = row[1]
            data_list.append({'timestamp': timestamp, 'data': data})


    return jsonify(data_list)

@app.route('/image/<timestamp1>/<timestamp2>', methods=['GET'])
def get_image(timestamp1, timestamp2):
    with db_conn.cursor() as cursor:
        sql = f"SELECT collect_time, collected_data from sensor_data WHERE collect_time={timestamp1} or collect_time={timestamp2}"
        print(sql)
        cursor.execute(sql)
        rows = cursor.fetchall()
        print(rows)
        data_list = []
        for row in rows:
            data = row[1]
            data_list.append(data)

    print(data_list)
    buffer = start_process(timestamp1, timestamp2, data_list)
    return send_file(buffer, mimetype='image/png')

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

def draw_same(waveform1, waveform2, timestamp1, timestamp2):
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

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    return buffer


def draw_diff(waveform1, waveform2, timestamp1, timestamp2):
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

    filename = timestamp1 + '_' + timestamp2 + '.png'
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    return buffer

def start_process(timestamp1, timestamp2, data_list):
    waveform1 = np.array([int(x) for x in data_list[0].split(',')])
    waveform2 = np.array([int(x) for x in data_list[1].split(',')])
    print(waveform1)
    print(waveform2)
    # Fimd time dealy of two waveforms
    time_delay = find_time_delay(waveform1, waveform2)

    # Adjust wavefrom2 relative to waveform1
    adjusted_waveform2 = adjust_phase(waveform1, waveform2, len(waveform2) - time_delay)

    # Check if two waveforms same.
    is_similar = check_similarity(waveform1, adjusted_waveform2)
    print(is_similar)
    if is_similar == True:
        buffer = draw_same(waveform1, waveform2, timestamp1, timestamp2)
    else:
        buffer = draw_diff(waveform1, waveform2, timestamp1, timestamp2)

    return buffer

def main(run_py_file):
    parser = argparse.ArgumentParser()
    parser.add_argument('--db_server', type=str, required=True, help="DB サーバアドレス")
    parser.add_argument('--db_user', type=str, required=True, help="DB User Name")
    parser.add_argument('--db_pass', type=str, required=True, help="DB Password")
    parser.add_argument('--sid', type=str, required=True, help='sid')
    parser.add_argument('--ssh_server', type=str, default='', help="ssh サーバアドレス")
    parser.add_argument('--ssh_user', type=str, default='', help="ssh User Name")
    parser.add_argument('--ssh_pass', type=str, default='', help="ssh Password")

    args = parser.parse_args()
    db_server = args.db_server
    db_user = args.db_user
    db_pass = args.db_pass
    sid = args.sid
    ssh_server = args.ssh_server
    ssh_user = args.ssh_user
    ssh_pass = args.ssh_pass
    db_conn, db_cur = connect_db(db_server, db_user, db_pass, sid, ssh_server, ssh_user, ssh_pass)
    app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    main(__file__)
    sys.exit(0)


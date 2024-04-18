import os
if os.name == 'nt':
    from sshtunnel import SSHTunnelForwarder
import pymysql.cursors

def connect_ssh(ssh_server, ssh_username, ssh_password, mysql_server):
    '''SSH接続'''
    if os.name == 'nt':
        server = SSHTunnelForwarder(
            (ssh_server, 22),
            ssh_host_key=None,
            ssh_username=ssh_username,
            ssh_password=ssh_password,
            remote_bind_address=(mysql_server, 3306)
        )
        server.start()
        return server

def connect_ssh_oracle(ssh_server, ssh_username, ssh_pkey, db_server):
    '''SSH接続'''
    if os.name == 'nt':
        server = SSHTunnelForwarder(
            (ssh_server, 22),
            ssh_host_key=None,
            ssh_username=ssh_username,
            ssh_password=None,
            ssh_pkey=ssh_pkey,
            remote_bind_address=(db_server, 1521),
        )
        # server.start()
        return server

def connect_mysql_db(server, mysql_server, username, password, sid):
    ''' db接続'''
    if server == None:
        conn = pymysql.connect(
            host=mysql_server,
            port=3306,
            user=username,
            password=password,
            database=sid,
            charset='utf8',
        )
    else:
        conn = pymysql.connect(
            host = '127.0.0.1',
            port = server.local_bind_port,
            user = username,
            password = password,
            database = sid,
            charset = 'utf8',
        )
    cur = conn.cursor()

    return conn, cur

# Disconnect mysql db
def disconnect_mysql_db(conn, cursor):
    if cursor != None:
        cursor.close()
    if conn != None:
        conn.close()

def connect_mysql(ssh_host, ssh_port, ssh_username, ssh_password, mysql_host, mysql_port, mysql_user, mysql_password, mysql_database):
    # Create SSH tunnel
    with SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_username,
            ssh_password=ssh_password,
            remote_bind_address=(mysql_host, mysql_port)
    ) as tunnel:
        # Connect to MySQL through the SSH tunnel
        connection = pymysql.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

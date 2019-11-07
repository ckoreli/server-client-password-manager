import socket
import select
import sqlite3
import string
import random
import datetime

HEADER_SIZE = 10

characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

db = sqlite3.connect("passwords.db")
c  = db.cursor()

f = open("server_log.txt", "a")

# c.execute("CREATE TABLE IF NOT EXISTS passwords(website TEXT, usr TEXT, passwd TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS users(usr TEXT, passwd TEXT)")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "192.168.0.33"
port = 1337

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, port))

server_socket.listen(5)

REFERAL = ""


def recv_msg(client_socket):
    try:
        msg_len = client_socket.recv(HEADER_SIZE)

        if not len(msg_len):
            return False

        msg_len = int(msg_len.decode("utf-8"))

        return client_socket.recv(msg_len).decode("utf-8")
    except:
        return False


def send_msg(client_socket, msg):

    msg = f"{len(msg) :< {HEADER_SIZE}}" + msg

    client_socket.send(msg.encode("utf-8"))    


def log(username, msg):
    print(f"[{datetime.datetime.now()}] '{username}' {msg}", file = f)

def log_error(username, msg):
    print(f"[{datetime.datetime.now()}] Error: '{username}' {msg}", file = f)

def save_pass(username, website, usr, passwd):

    c.execute(f"INSERT INTO {username}(website, usr, passwd) VALUES(?, ?, ?)", (website, usr, passwd))
    db.commit()

    print("Password successfuly saved.")
    log(username, "saved password to table.")

def set_pass(username, website, passwd):
    try:
        c.execute(f"SELECT passwd FROM {username} WHERE website = '{website}'")
        old_passwd = c.fetchall()[0][0]

        c.execute(f"UPDATE {username} SET passwd = '{passwd}' WHERE website = '{website}'")
        db.commit()

        log(username, "setting new value for existing password.")

        return "1"
    except:
        log_error(username, "tried to change nonexisting password.")
        return "0"

def get_pass(username, website):

    c.execute(f"SELECT usr, passwd FROM {username} WHERE website='{website}'")
    try:
        ret = c.fetchall()[0]
        log(username, "fetching password.")
        return ret[0], ret[1]
    except:
        log_error(username, "tried to fetch nonexisting password.")
        return 0, 0

def delete_pass(username, website):

    c.execute(f"DELETE FROM {username} WHERE website = '{website}'")
    db.commit()

    log(username, "deleted password.")


def generate_code():
    REFERAL_CODE = ""
    for i in range(10):
        REFERAL_CODE += random.choice(characters)

    return REFERAL_CODE



def login(username, password):
    try:
        # print("Proveravam informacije...")
        c.execute(f"SELECT passwd FROM users WHERE usr='{username}'")
        passwd = c.fetchall()[0][0]
        # print(passwd)
        
        return password == passwd
    except:
        return False


def register(client_, username, password):
    try:
        c.execute(f"SELECT usr FROM users WHERE usr='{username}'")
        temp = c.fetchall()[0][0]
        
        return "0"

    except:
        c.execute(f"CREATE TABLE IF NOT EXISTS {username}(website TEXT, usr TEXT, passwd TEXT)")
        # db.commit()
        c.execute(f"INSERT INTO users(usr, passwd) VALUES(?, ?)", (username, password))
        db.commit()

        logged_in_clients[client_] = username
        log(username, "registered successfuly.")
        return "1"


socket_list = [server_socket]
logged_in_clients = {}

REFERAL = generate_code()
print(f"Current referal code : {REFERAL}")

while True:
    read_sockets, _, exception_sockets = select.select(socket_list, [], socket_list)
    for notified in read_sockets:
        if notified == server_socket:
            client_socket, client_address = server_socket.accept()

            socket_list.append(client_socket)

            print(f"Received connection from {client_address}")

        else:
            command = recv_msg(notified)

            if command is False:
                socket_list.remove(notified)
                if notified in logged_in_clients:
                    log(logged_in_clients[notified], "has left the server.")
                    del logged_in_clients[notified]
                print("Client disconnected.")
                continue
            
            print(f"Executing {command} command.")

            if command == "register":
                username = recv_msg(notified)
                password = recv_msg(notified)
                code = recv_msg(notified)

                # print(f"{code} == {REFERAL}")
                # print(code == REFERAL)

                success = "1"
                if code != REFERAL:
                    success = "0"
                
                send_msg(notified, success)
                if int(success):

                    # print("Username = " + username)
                    # print("Password = " + password)

                    success = register(notified, username, password)
                    if success == "1":
                        REFERAL = generate_code()
                        print(f"Current referal code : {REFERAL}")
                    
                    send_msg(notified, success)

                else:
                    print("Incorrect referal code.")
                    log_error("", "Attempted registration with incorrect referal code.")

            elif command == "login":
                username = recv_msg(notified)
                password = recv_msg(notified)

                success = "1"

                # print(username, password)

                if login(username, password):
                    send_msg(notified, success)
                    logged_in_clients[notified] = username
                    log(username, "has joined the server.")

                else:
                    log(username, "attempted to log in.")
                    success = "0"
                    send_msg(notified, success)

            # print(logged_in_clients[notified])
            # print(logged_in_clients)
            if not notified in logged_in_clients:
                continue    

            if command == "set":
                website = recv_msg(notified)
                password = recv_msg(notified)

                success = set_pass(logged_in_clients[notified], website, password)
                send_msg(notified, success)

            elif command == "save":
                website = recv_msg(notified)
                username = recv_msg(notified)
                password = recv_msg(notified)

                save_pass(logged_in_clients[notified], website, username, password)

            elif command == "delete":
                website = recv_msg(notified)
                
                delete_pass(logged_in_clients[notified], website)

            elif command == "get":
                website = recv_msg(notified)

                username, password = get_pass(logged_in_clients[notified], website)

                error = "0"

                if not username:
                    error = "1"
                    send_msg(notified, error)
                    print("Error: User asked for nonexisting password.")
                    continue

                send_msg(notified, error)
                send_msg(notified, username)
                send_msg(notified, password)

            elif command == "logout":
                log(logged_in_clients[notified], "has left the server.")
                del logged_in_clients[notified]


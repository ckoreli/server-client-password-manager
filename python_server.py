import socket
import select
import sqlite3

HEADER_SIZE = 10

db = sqlite3.connect("passwords.db")
c  = db.cursor()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "192.168.0.33"
port = 1337

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, port))

server_socket.listen(5)


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


def save_pass(website, usr, passwd):

    c.execute("INSERT INTO passwords(website, usr, passwd) VALUES(?, ?, ?)", (website, usr, passwd))
    db.commit()

    print("Password successfuly saved.")

def set_pass(website, passwd):

    c.execute(f"SELECT passwd FROM passwords WHERE website = '{website}'")
    old_passwd = c.fetchall()[0][0]

    c.execute(f"UPDATE passwords SET passwd = '{passwd}' WHERE website = '{website}'")
    db.commit()

def get_pass(website):

    c.execute(f"SELECT usr, passwd FROM passwords WHERE website='{website}'")
    try:
        ret = c.fetchall()[0]
        return ret[0], ret[1]
    except:
        return 0, 0

def delete_pass(website):

    c.execute(f"DELETE FROM passwords WHERE website = '{website}'")
    db.commit()


socket_list = [server_socket]
clients = {}

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
                print("Client disconnected.")
                continue
            
            print(f"Executing {command} command.")

            if command == "set":
                website = recv_msg(notified)
                password = recv_msg(notified)

                set_pass(website, password)

            elif command == "save":
                website = recv_msg(notified)
                username = recv_msg(notified)
                password = recv_msg(notified)

                save_pass(website, username, password)

            elif command == "delete":
                website = recv_msg(notified)
                
                delete_pass(website)

            elif command == "get":
                website = recv_msg(notified)

                username, password = get_pass(website)

                error = "0"

                if not username:
                    error = "1"
                    send_msg(notified, error)
                    print("Error: User asked for nonexisting password.")
                    continue

                send_msg(notified, error)
                send_msg(notified, username)
                send_msg(notified, password)


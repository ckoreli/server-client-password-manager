import socket

HEADER_SIZE = 10
WELCOME_WIDTH = 26

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "192.168.0.33"
port = 1234

client_socket.connect((host, port))

start = True


def recv_msg():
    # print("Receiving message")
    msg_size = int(client_socket.recv(HEADER_SIZE).decode("utf-8"))
    # print(f"Message size = {msg_size}")
    msg = client_socket.recv(msg_size).decode("utf-8")
    # print("Message = " + msg)
    return msg

def send_msg(msg):
    header = f"{len(msg) :< {HEADER_SIZE}}"
    client_socket.send(header.encode("utf-8"))
    client_socket.send(msg.encode("utf-8"))

def recv_welcome():
    for i in range(4):
        line = client_socket.recv(WELCOME_WIDTH).decode("utf-8")
        print(line)

def recv_menu():
    for i in range(10):
        line = client_socket.recv(WELCOME_WIDTH).decode("utf-8")
        print(line)


while True:
    if start:
        recv_welcome()
        recv_menu()
        start = False
    command = input("> ")
    send_msg(command)
    if command == 's':
        website = input("Website: ")
        send_msg(website)

        username = input("Username: ")
        send_msg(username)
        
        password = input("Password: ")
        send_msg(password)

        print("Saving password...")
    elif command == 'c':
        website = input("Website: ")
        password = input("New password: ")
        send_msg(website)
        send_msg(password)
        print(f"Successfuly changed password for {website}")
    elif command == 'g':
        website = input("Website: ")
        send_msg(website)
        password = recv_msg()
        print(f"Password for {website} : {password}")
    elif command == 'd':
        website = input("Website: ")
        send_msg(website)
        print("Deleting...")
    elif command == 'q':
        print("Quitting...")
        break

client_socket.close()

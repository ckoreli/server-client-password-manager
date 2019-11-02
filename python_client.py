import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "192.168.0.33"
port = 1234

s.connect((host, port))

while True:
    print(s.recv(1024).decode("utf-8"))
    msg = input("> ");
    s.send(msg.encode("utf-8"));
import socket
import sqlite3

print("Initializing server...")

WEBSITE = 0
USR = 1
PASSWD = 2

HEADER_SIZE = 10

db = sqlite3.connect("passwords.db")
c = db.cursor()

c.execute("CREATE TABLE IF NOT EXISTS passwords(website TEXT, usr TEXT, passwd TEXT)")

# Napravi novi socket object koji interaguje preko IP (socket.AF_INET) pomocu TCP protokola (socket.SOCK_STREAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Set socket option da port koji odredim bude reusable
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#                             GDE                  STA          NA
host = "192.168.0.33"
port = 1234
# Bindujem host i port na kojem treba da slusa za socket
server_socket.bind((host, port));
# Cekam neku konekciju (max 5)
server_socket.listen(5);
client_socket = False


def recv_msg():
    print("Receiving message")
    msg_size = int(client_socket.recv(HEADER_SIZE).decode("utf-8"))
    print(f"Message size = {msg_size}")
    msg = client_socket.recv(msg_size).decode("utf-8")
    print("Message = " + msg)
    return msg

def send_msg(msg):
    header = f"{len(msg) :< {HEADER_SIZE}}"
    # print("Message = " + msg)
    client_socket.send(header.encode("utf-8"))
    client_socket.send(msg.encode("utf-8"))

def print_welcome():
    welcome_msg = ["##########################",
                   "#                        #",
                   "# Welcome to the server. #",
                   "#                        #"]
    for line in welcome_msg:
        # print(line)
        client_socket.send(line.encode("utf-8"))
        # sleep(1)

def print_menu():
    menu = ["##########################",
            "#                        #",
            "# Get password......[g]  #",
            "# Save password.....[s]  #",
            "# Change password...[c]  #",
            "# Delete password...[d]  #",
            "# Generate password.[g]  #",
            "# Quit..............[q]  #",
            "#                        #",
            "##########################"]
    for line in menu:
        # print(line);
        client_socket.send(line.encode("utf-8"))
        # sleep(1)

def save_pass(website, usr, passwd):
    print(passwd)

    c.execute("INSERT INTO passwords(website, usr, passwd) VALUES(?, ?, ?)", (website, usr, passwd))
    db.commit()

    print("Password successfuly saved.")

def change_pass(website, passwd):

    c.execute(f"SELECT passwd FROM passwords WHERE website = '{website}'")
    old_passwd = c.fetchall()[0][0]

    c.execute(f"UPDATE passwords SET passwd = '{passwd}' WHERE website = '{website}'")
    db.commit()

def get_pass(website):

    c.execute(f"SELECT passwd FROM passwords WHERE website='{website}'")

    return c.fetchall()[0][0]

def generate_pass():
    pass

def delete_pass(website):

    c.execute(f"DELETE FROM passwords WHERE website = '{website}'")
    db.commit()

print("Server successfuly initialized. Listening...")

while True:
    if not client_socket:
        client_socket, address = server_socket.accept()
        print(f"{address} has connected.")
        print_welcome()
        print_menu()
    
    command = client_socket.recv(1).decode("utf-8")
    if command == 's':
        website = recv_msg()
        usr = recv_msg()
        passwd = recv_msg()
        save_pass(website, usr, passwd)
        print(f"Saved new password for website: {website}.")
    elif command == 'g':
        website = recv_msg()
        pas = get_pass(website)
        print(f"Getting password for website: {website}.")
        send_msg(pas)
    elif command == 'c':
        website = recv_msg()
        passwd = recv_msg()
        print(f"Changing password for website: {website}.")
        change_pass(website, passwd)
    elif command == 'd':
        website = recv_msg()
        print(f"Deleting password for website: {website}.")
        delete_pass(website)
    elif command == 'q':
        print("Client disconnecting...")
        client_socket.close()
        client_socket = False

c.close()
db.close()
client_socket.close()

#########################
#                       #
# DOBRO DOSAO NA SERVER #
#                       #
#########################
#                       #
# IZABERI USLUGU:       #
# >SACUVAJ NOVU SIFRU[s]#
# >OCITAJ POSTOJECU[g]  #
# >PROMENI POSTOJECU[c] #
# >OBRISI SIFRU[d]      #
# >GENERISI SIFRU[g]    #
#                       #
#########################
# >

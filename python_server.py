import socket
import sqlite3

WEBSITE = 0
USR = 1
PASSWD = 2

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
# server_socket.bind((host, port));
# Cekam neku konekciju (max 5)
# server_socket.listen(5);


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


while True:
    check = input("Da li zelis nes da uradis? (d/n) ")
    if check == 'n':
        break
    option = input("Sta bi zeleo?")
    if option == 's':
        website = input("Unesi ime sajta: ")
        usr = input("Unesi username: ")
        passwd = input("Unesi password: ")
        save_pass(website, usr, passwd)
    if option == 'g':
        website = input("Unesi ime sajta: ")
        pas = get_pass(website)
        print(pas)
    if option == 'c':
        website = input("Unesi ime sajta: ")
        passwd = input("Unesi novi password: ")
        change_pass(website, passwd)
    if option == 'd':
        website = input("Unesi ime sajta: ")
        delete_pass(website)

c.close()
db.close()
import socket
import random
import sys

HEADER_SIZE = 10

unicorn = ["              ,,))))))));,",
           "           __)))))))))))))),",
           "\|/       -\(((((''''((((((((.",
           "-*-==//////((''  .     `)))))),",
           "/|\      ))| o    ;-.    '(((((                                  ,(,",
           "         ( `|    /  )    ;))))'                               ,_))^;(~",
           "            |   |   |   ,))((((_     _____------~~~-.        %,;(;(>';'~",
           "            o_);   ;    )))(((` ~---~  `::           \      %%~~)(v;(`('~",
           "                  ;    ''''````         `:       `:::|\,__,%%    );`'; ~",
           "                 |   _                )     /      `:|`----'     `-'",
           "           ______/\/~    |                 /        /",
           "         /~;;.____/;;'  /          ___--,-(   `;;;/",
           "        / //  _;______;'------~~~~~    /;;/\    /",
           "       //  | |                        / ;   \;;,\\",
           "      (<_  | ;                      /',/-----'  _>",
           "       \_| ||_                     //~;~~~~~~~~~",
           "           `\_|                   (,~~  -Tua Xiong",
           "                                   \~\\",
           "                                    ~~"]

for line in unicorn:
    print(line)

print("Password manager, version 2.3\nType 'help' for full list of builtin commands and their descriptions.")

characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(){}[]:|/,.<>;=+_-~'

commands = {"login" : {"arguments" : 2},
            "logout" : {"arguments" : 0},
            "register" : {"arguments" : 3},
            "get" : {"arguments" : 1}, 
            "set" : {"arguments" : 2}, 
            "save" : {"arguments" : 3}, 
            "delete" : {"arguments" : 1}, 
            "quit" : {"arguments" : 0}, 
            "generate" : {"arguments" : 1},
            "help" : {"arguments" : 1},
            "whoami" : {"arguments" : 0}}

help_ = {"header" : "Password manager, version 2.0\nThese commands are defined internally. Type 'help name' to find out more about command 'name'.\n",
         "login" : "\tlogin: login [USERNAME] [PASSWORD]  -  Log in to service as USERNAME.\n",
         "logout" : "\tlogout: logout  -  Log out.\n",
         "register" : "\tregister : register [USERNAME] [PASSWORD] [REFERAL CODE]  -  Register new user to service.\n",
         "whoami" : "\twhoami: whoami  -  Prints username of currently logged in account.\n",
         "get" : "\tget: get [WEBSITE]  -  Get saved password for WEBSITE.\n",
         "set" : "\tset: set [WEBSITE]  -  Set new password for WEBSITE.\n",
         "save" : "\tsave: save [WEBSITE] [USERNAME] [PASSWORD]  -  Save PASSWORD for WEBSITE with USERNAME into database.\n",
         "delete" : "\tdelete: delete [WEBSITE]  -  Delete saved password for WEBSITE.\n", 
         "generate" : "\tgenerate: generate [LENGTH]  -  Generates a relatively safe, random password.\n",
         "help" : "\thelp: help [COMMAND]  -  Display information about builtin COMMAND. Leave blank for full list of builtin commands.\n",
         "quit" : "\tquit: quit  -  Finish current session.\n"}

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "192.168.0.33"
port = 1337

client_socket.connect((host, port))

logged_in = False
logged_as = ""


def generate(length):
    random_pass = ""
    for i in range(length):
        random_pass += random.choice(characters)

    print(random_pass)


def check(command):
    if command[0] not in commands:
        print(f"Command '{command[0]}' not found. Try 'help' for full list of builtin commands.")
        return False

    if command[0] == 'help':
        if len(command) > 2:
            print("Invalid syntax for command 'help'. Try: 'help help'.")
            return False
    
    elif len(command) - 1 != commands[command[0]]["arguments"]:
        print(f"Invalid syntax for command '{command[0]}'. Try: 'help {command[0]}'")
        return False
    
    return True


def send_msg(msg):
    try:
        msg = f"{len(msg) :< {HEADER_SIZE}}" + msg

        client_socket.send(msg.encode("utf-8"))
    except:
        print("Server disconnected.")
        sys.exit()


def send_command(command):

    for word in command:
        send_msg(word)


def recv_msg():
    try:
        msg_len = client_socket.recv(HEADER_SIZE)

        if not len(msg_len):
            return False

        msg_len = int(msg_len.decode("utf-8"))

        return client_socket.recv(msg_len).decode("utf-8")
    except:
        return False


while True:
    command = input("# ").split()
    if not check(command):
        continue
    if command[0] == 'help':
        if len(command) == 1:
            for key, value in help_.items():
                print(value)
        else:
            print()
            print(help_.get(command[1]))
    
    else:
        if command[0] == "whoami":
            if logged_in:
                print(f"Currently logged in as '{logged_as}'")
            else:
                print("You are not logged in.")
            continue

        elif command[0] == "quit":
            print("Disconnecting.")
            break

        if not logged_in and (command[0] != "login" and command[0] != "register"):
            print("You need to be logged in in order to use the service.")
            continue

        elif command[0] == "login":
            if logged_in:
                print("You are already logged in.")
            
            else:
                send_command(command)
                username = command[1]
                success = int(recv_msg())

                if not success:
                    print("Incorrect username or password.")
                
                else:
                    print(f"Successfuly logged in as '{username}'.")
                    logged_in = True
                    logged_as = username

        elif command[0] == "register":
            if logged_in:
                print("Log out before registering a new account.")

            else:
                send_command(command)
                success = int(recv_msg())

                if not success:
                    print("Incorrect referal key, contact server administrator if you wish to register an account.")
                
                else:
                    success = int(recv_msg())
                    if success:
                        print("Successfuly registered new account.")
                        logged_in = True
                        logged_as = command[1]
                    else:
                        print(f"Account '{command[1]}' is already registered.")

        elif command[0] == "logout":
            send_command(command)
            logged_in = False
            logged_as = ""
        
        elif command[0] == "get":
            send_command(command)
            error = recv_msg()
            if int(error):
                print(f"Error: Asking for nonexisting password.")

            else:
                print(f"Credentials for '{command[1]}':")
                username = recv_msg()
                password = recv_msg()

                print(f"\tUsername: {username}\n\tPassword: {password}") 


        elif command[0] == "set":
            send_command(command)
            success = int(recv_msg())
            if success:
                print(f"Changing password for '{command[1]}'.")
            else:
                print("Error: Trying to change nonexisting password.")

        elif command[0] == "save":
            send_command(command)
            print(f"Saving new password for '{command[1]}'.")
        
        elif command[0] == "delete":
            send_command(command)
            print(f"Deleting password for '{command[1]}'.")
        
        elif command[0] == "generate":
            generate(int(command[1]))

client_socket.close()

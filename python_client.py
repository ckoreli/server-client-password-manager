import socket

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
           "           `\_|                   (,~~",
           "                                   \~\\",
           "                                    ~~"]

for line in unicorn:
    print(line)

print("Password manager, version 2.0\nType 'help' for full list of builtin commands and their descriptions.")

commands = {"get" : {"arguments" : 1}, 
            "set" : {"arguments" : 2}, 
            "save" : {"arguments" : 3}, 
            "delete" : {"arguments" : 1}, 
            "quit" : {"arguments" : 0}, 
            "generate" : {"arguments" : 0},
            "help" : {"arguments": 1}}

help_ = {"header" : "Password manager, version 2.0\nThese commands are defined internally. Type 'help name' to find out more about command 'name'.\n",
         "get" : "\tget: get [WEBSITE]  -  Get saved password for WEBSITE.\n",
         "set" : "\tset: set [WEBSITE]  -  Set new password for WEBSITE.\n",
         "save" : "\tsave: save [WEBSITE] [USERNAME] [PASSWORD]  -  Save PASSWORD for WEBSITE with USERNAME into database.\n",
         "delete" : "\tdelete: delete [WEBSITE]  -  Delete saved password for WEBSITE.\n", 
         "generate" : "\tgenerate: generate  -  Generates a relatively safe, random password.\n",
         "help" : "\thelp: help [COMMAND]  -  Display information about builtin COMMAND. Leave blank for full list of builtin commands.\n",
         "quit" : "\tquit: quit  -  Finish current session.\n"}

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "192.168.0.33"
port = 1337

client_socket.connect((host, port))


def generate():
    pass


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
    
    msg = f"{len(msg) :< {HEADER_SIZE}}" + msg

    client_socket.send(msg.encode("utf-8"))


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
        send_command(command)

        if command[0] == "get":
            error = recv_msg()
            if int(error):
                print(f"Error: Asking for nonexisting password.")

            else:
                print(f"Credentials for '{command[1]}':")
                username = recv_msg()
                password = recv_msg()

                print(f"\tUsername: {username}\n\tPassword: {password}") 


        elif command[0] == "set":
            print(f"Changing password for '{command[1]}'.")

        elif command[0] == "save":
            print(f"Saving new password for '{command[1]}'.")
        
        elif command[0] == "delete":
            print(f"Deleting password for '{command[1]}'.")
        
        elif command[0] == "generate":
            pass
        
        elif command[0] == "quit":
            print("Disconnecting.")
            break




client_socket.close()

# import socket
import threading
from socket import *

# SERVER_ADDRESS = ('localhost', 13000)
# TODO: figure out why we have to put specific ip instead of 'localhost'!
serverName = '10.0.0.10'


def get_users():
    clientSocket.send("<get_users>".encode())


def disconnect():
    clientSocket.send("<disconnect>".encode())
    server_feedback = clientSocket.recv(1024).decode()


def set_msg():
    other_user = input("Input username: ")
    msg = input("Input message: ")
    set_msg_request = "<set_msg><" + other_user + "><" + msg + ">"
    clientSocket.send(set_msg_request.encode())


def set_msg_all():
    msg = input("Input message: ")
    set_msg_all_request = "<set_msg_all><" + msg + ">"
    clientSocket.send(set_msg_all_request.encode())


def show_all_msg():
    clientSocket.send("<show_all_msgs>".encode())


def get_list_file():
    return "h"


def download():
    return "h"


def proceed():
    return "h"


def switcher(action):
    if action == 1:
        get_users()
    elif action == 2:
        disconnect()
    elif action == 3:
        set_msg()
    elif action == 4:
        set_msg_all()
    elif action == 5:
        show_all_msg()
    elif action == 6:
        get_list_file()
    elif action == 7:
        download()
    elif action == 8:
        proceed()
    else:
        return "Invalid action"


while True:
    clientInput = input("Enter port number between 55000 to 55015: ")
    # checking if input is a number
    try:
        clientPort = int(clientInput)
        # checking if the port is out of bounds
        if 55000 <= clientPort <= 55016:
            # checking if specific port is available
            try:
                SERVER_ADDRESS = (serverName, 50000)
                clientSocket = socket(AF_INET, SOCK_STREAM)
                clientSocket.bind(('0.0.0.0', clientPort))
                clientSocket.connect(SERVER_ADDRESS)
                feedback = clientSocket.recv(1024).decode()
                break
            except OSError as e:
                # error number 10048 = Port is taken,
                # Only one usage of each socket address is normally permitted
                if e.errno == 10048:
                    print("Port is unavailable, Please try another one!")
        else:
            print("Port out of range!\n")
    except ValueError:
        print("Please enter numeric value!\n")


def menu():
    print("Action menu: \n")
    print("1- get users list\n")
    print("2- disconnect\n")
    print("3- send private message\n")
    print("4- send message to all online users\n")
    print("5- show all messages\n")
    print("6- get list of files\n")
    print("7- download file\n")
    print("8- proceed\n")


def receive_msgs(clientsocket):

    while True:
        # message="<name><msg>"
        buffer = clientSocket.recv(1024)
        if buffer:
            message = buffer.decode()

            # get users
            if message.startswith("<users_lst>"):
                message = message[12:]
                # server_feedback = "num_of_users><user1><user2>...<end>
                index = message.find(">")
                num_of_usr = message[0:index]
                print("Number of users connected: " + num_of_usr + "\nthe users:")
                message = message[index + 1:]
                # server_feedback = "<usr1><usr2>...<end>
                for _ in range(int(num_of_usr)):
                    index = message.find(">")
                    user = message[1:index]
                    print(user + "\n")
                    message = message[index + 1:]

            # connect
            elif feedback == "<connection_established>":
                print("connection established\n")

            # disconnect
            elif message.startswith("<disconnected>"):
                print("Successfully disconnected\n")
                clientSocket.close()
                exit()

            # send message
            elif message.startswith("<message_to_yourself>"):
                print("You can't send a message to yourself\n")

            elif message.startswith("<msg_sent>"):
                print("Message sent successfully!\n")

            elif message.startswith("<invalid_name>"):
                print("The name you chose is not in the chatroom!\n")

            # show all messages
            elif message.startswith("<no_msgs>"):
                print("You have no messages yet\n")

            elif message.startswith("<msg_lst>"):
                message = message[10:]
                # message = "num_of_msgs><msg1><msg2>...<end>"
                index = message.find(">")
                num_of_msgs = message[0:index]
                print("Number of messages: " + num_of_msgs + "\nthe messages are:")
                message = message[index + 1:]
                # message = "<msg1><msg2>...<end>
                for _ in range(int(num_of_msgs)):
                    index = message.find(">")
                    msg = message[1:index]
                    print(msg + "\n")
                    message = message[index + 1:]


def actions():
    while True:
        client_input = input("Please select action: \n")
        # checking if input is a number
        try:
            action = int(client_input)
            if int(action) < 1 or int(action) > 8:
                print("Please choose number between 1 to 8\n")
            else:
                switcher(action)
        except ValueError:
            print("Please enter numeric value!\n")


while True:
    username = input("Input username: ")
    connect_request = "<connect><" + username + ">"
    # clientSocket.send(bytes(sentence, encoding="UTF-8"))
    clientSocket.send(connect_request.encode())
    print("Thank you!\n")
    break
menu()
t1 = threading.Thread(target=actions)
t2 = threading.Thread(target=receive_msgs, args=(clientSocket,))

t2.start()
t1.start()
t2.join()
t1.join()






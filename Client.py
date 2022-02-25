# import socket
import _thread
import errno
import sys
import threading
from _thread import start_new_thread
from socket import *

# SERVER_ADDRESS = ('localhost', 13000)
# TODO: figure out why we have to put specific ip instead of 'localhost'!
serverName = '10.0.0.10'

clients_lock = threading.Lock()


def print_msg(server_feedback: str):
    if server_feedback.startswith("<msg>"):
        server_feedback = server_feedback[5:]
        # message="<name><msg>"
        index = server_feedback.find(">")
        name = server_feedback[1:index]
        msg = server_feedback[index + 1:-1]
        print(name + ": " + msg)
        return True
    else:
        return False


def get_users():
    with clients_lock:
        clientSocket.send("<get_users>".encode())
        server_feedback = clientSocket.recv(1024).decode()
        if print_msg(server_feedback):
            server_feedback = clientSocket.recv(1024).decode()
        # server_feedback = "<users_list><num_of_users><user1><user2>...<end>
        server_feedback = server_feedback[12:]
        # server_feedback = "num_of_users><user1><user2>...<end>
        index = server_feedback.find(">")
        num_of_usr = server_feedback[0:index]
        print("Number of users connected: " + num_of_usr + "\nthe users:")
        server_feedback = server_feedback[index + 1:]
        # server_feedback = "<usr1><usr2>...<end>
        for _ in range(int(num_of_usr)):
            index = server_feedback.find(">")
            user = server_feedback[1:index]
            print(user + "\n")
            server_feedback = server_feedback[index + 1:]


def disconnect():
    with clients_lock:
        clientSocket.send("<disconnect>".encode())
        server_feedback = clientSocket.recv(1024).decode()
        if server_feedback == "<disconnected>":
            print("Successfully disconnected\n")
            clientSocket.close()
            exit()


def set_msg():
    with clients_lock:
        other_user = input("Input username: ")
        msg = input("Input message: ")
        set_msg_request = "<set_msg><" + other_user + "><" + msg + ">"
        clientSocket.send(set_msg_request.encode())
        server_feedback = clientSocket.recv(1024).decode()
        if print_msg(server_feedback):
            server_feedback = clientSocket.recv(1024).decode()
        if server_feedback == "<message_to_yourself>":
            print("You can't send a message to yourself\n")
        else:
            if server_feedback == "<msg_sent>":
                print("Message sent successfully!\n")
                print("Me:" + msg)
            elif server_feedback == "<invalid_name>":
                print("The name you chose is not in the chatroom!\n")
            else:
                print(server_feedback)


def set_msg_all():
    with clients_lock:
        msg = input("Input message: ")
        set_msg_all_request = "<set_msg_all><" + msg + ">"
        clientSocket.send(set_msg_all_request.encode())
        server_feedback = clientSocket.recv(1024).decode()
        if print_msg(server_feedback):
            server_feedback = clientSocket.recv(1024).decode()
        if server_feedback == "<msg_sent>":
            print("Message sent successfully!\n")
            print("Me:" + msg)


def show_all_msg():
    with clients_lock:
        clientSocket.send("<show_all_msgs>".encode())
        server_feedback = clientSocket.recv(1024).decode()
        if print_msg(server_feedback):
            server_feedback = clientSocket.recv(1024).decode()
        if server_feedback == "<no_msgs>":
            print("You have no messages yet\n")
        else:
            # server_feedback = "<msg_lst><num_of_msgs><msg1><msg2>...<end>"
            server_feedback = server_feedback[10:]
            # server_feedback = "num_of_msgs><msg1><msg2>...<end>"
            index = server_feedback.find(">")
            num_of_msgs = server_feedback[0:index]
            print("Number of messages: " + num_of_msgs + "\nthe messages are:")
            server_feedback = server_feedback[index + 1:]
            # server_feedback = "<msg1><msg2>...<end>
            for _ in range(int(num_of_msgs)):
                index = server_feedback.find(">")
                msg = server_feedback[1:index]
                print(msg + "\n")
                server_feedback = server_feedback[index + 1:]


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
                if feedback == "<connection_established>":
                    print("connection established\n")
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
        if not buffer:
            break
        message = buffer.decode()
        index = message.find(">")
        name = message[1:index]
        msg = message[index + 1:-1]
        print(name + ": " + msg)


def actions():
    while True:
        client_input = input("Please select action: ")
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
    feedback = clientSocket.recv(1024).decode()
    if feedback == "<connected>":
        print("Thank you!\n")
        menu()
        # actions()
        flag = threading.Thread(target=actions())
        threading.Thread(target=receive_msgs())

        break
    elif feedback == "<available_name>":
        print("User name is taken!\n")

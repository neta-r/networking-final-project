# import socket
from socket import *

# SERVER_ADDRESS = ('localhost', 13000)
# TODO: figure out why we have to put specific ip instead of 'localhost'!
serverName = '10.80.4.238'


def get_users():
    clientSocket.send("<get_users>".encode())
    server_feedback = clientSocket.recv(1024).decode()
    # server_feedback = "<users_list><num_of_users><msg1><msg2>...<end>
    server_feedback = server_feedback[13:-1]
    # server_feedback = "num_of_users><msg1><msg2>...<end>
    index = server_feedback.find(">")
    num_of_msg = server_feedback[0:index - 1]
    print("You have " + num_of_msg + " messages: \n")
    server_feedback = server_feedback[index + 2:-1]
    # server_feedback = "msg1><msg2>...<end>
    for _ in range[0:num_of_msg]:
        index = server_feedback.find(">")
        msg = server_feedback[0:index - 1]
        print(msg+"\n")
        server_feedback = server_feedback[index + 1:-1]


def disconnect():
    clientSocket.send("<disconnect>".encode())
    server_feedback = clientSocket.recv(1024).decode()
    if server_feedback == "<disconnected>":
        print("Successfully disconnected\n")


def set_msg():
    other_user = input("Input username: ")
    msg = input("Input message: ")
    set_msg_request = "<set_msg><" + other_user + "><" + msg + ">"
    clientSocket.send(set_msg_request.encode())
    server_feedback = clientSocket.recv(1024).decode()
    if server_feedback == "<msg_sent>":
        print("Message sent successfully!\n")
    elif server_feedback == "<invalid_name>":
        print("The name you chose is not in the chatroom!\n")


def set_msg_all():
    msg = input("Input message: ")
    set_msg_all_request = "<set_msg><" + msg + ">"
    clientSocket.send(set_msg_all_request.encode())
    server_feedback = clientSocket.recv(1024).decode()
    if server_feedback == "<msg_sent>":
        print("Message sent successfully!\n")


def get_list_file():
    return "h"


def download():
    return "h"


def proceed():
    return "h"


def actions(action):
    switcher = {
        "get_users": get_users(),
        "disconnect": disconnect(),
        "set_msg": set_msg(),
        "set_msg_all": set_msg_all(),
        "get_list_file": get_list_file(),
        "download": download(),
        "proceed": proceed()
    }
    return switcher.get(action, "Invalid action")


while True:
    clientPort = input("Enter port number between 55000 to 55015: ")
    SERVER_ADDRESS = (serverName, 50000)
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.bind(('0.0.0.0', int(clientPort)))
    clientSocket.connect(SERVER_ADDRESS)
    feedback = clientSocket.recv(1024).decode()
    if feedback == "<connection_established>":
        print("connection established\n")
        break
    elif feedback == "<port_out_of_range>":
        print("Port out of range!\n")
    elif feedback == "<port_unavailable>":
        print("Chosen port is taken! Please select another one\n")

while True:
    username = input("Input username: ")
    connect_request = "<connect><" + username + ">"
    # clientSocket.send(bytes(sentence, encoding="UTF-8"))
    clientSocket.send(connect_request.encode())
    feedback = clientSocket.recv(1024).decode()
    if feedback == "<connected>":
        print("Thank you!\n")
        break
    elif feedback == "<available_name>":
        print("User name is taken!\n")

while True:
    print("Action menu: \n")
    print("1- get users list\n")
    print("2- disconnect\n")
    print("3- send private message\n")
    print("4- send message to all online users\n")
    print("5- get list of files\n")
    print("6- download file\n")
    print("7- proceed\n")
    action = input("Please select action: ")
    if int(action) < 1 or int(action) > 7:
        print("Please choose number between 1 to 7\n")
    else:
        actions(action)
        if action == 2:
            break
clientSocket.close()

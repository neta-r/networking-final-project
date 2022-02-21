# client's Port: (client's IP, client's user name, client's connection, client's list of massages)
from _thread import start_new_thread
# import socket module
from socket import *
import sys  # In order to terminate the program

num_of_threads = 0
available_ports = {"55000": (str, str, 0, [str]), "55001": (str, str, 0, [str]), "55002": (str, str, 0, [str]),
                   "55003": (str, str, 0, [str]), "55004": (str, str, 0, [str]), "55005": (str, str, 0, [str]),
                   "55006": (str, str, 0, [str]), "55007": (str, str, 0, [str]), "55008": (str, str, 0, [str]),
                   "55009": (str, str, 0, [str]), "55010": (str, str, 0, [str]), "55011": (str, str, 0, [str]),
                   "55012": (str, str, 0, [str]), "55013": (str, str, 0, [str]), "55014": (str, str, 0, [str]),
                   "55015": (str, str, 0, [str])}


# connect to chat! In this point we already have a connection to the server
def connect(name, port, ip):
    available_ports[port][0] = ip
    available_ports[port][1] = name
    available_ports[port][2] = connectionSocket
    connectionSocket.send('<connected>'.encode())
    print(name + " connected")


# message_send- is the massage according to protocol
# online_users_print- will display on the screen
def get_users():
    online_users_print = str
    online_users_send = str
    for val in available_ports.values():
        if val[2] != 0:
            online_users_print += val[1] + ","
            online_users_send += "<" + str(val[1]) + ">"

    print(online_users_print[0:-2])
    message_send = "<users_lst><" + str(num_of_threads) + ">" + str(online_users_send) + "<end>"
    connectionSocket.send(message_send.encode())


# we need to free the port
def disconnect(port):
    connectionSocket.send("<disconnected>".encode())
    available_ports[port] = ("", "", 0, [str])


def set_msg():
    return "h"


def set_msg_all():
    return "h"


def get_list_file():
    return "h"


def download():
    return "h"


def proceed():
    return "h"


def actions(action, rest_of_msg, port, ip):
    switcher = {
        "connect": connect(rest_of_msg, port, ip),
        "get_users": get_users(),
        "disconnect": disconnect(port),
        "set_msg": set_msg(),
        "set_msg_all": set_msg_all(),
        "get_list_file": get_list_file(),
        "download": download(),
        "proceed": proceed()
    }
    return switcher.get(action, "Invalid action")


# Given server port
serverPort = 50000
# choosing type of protocol
# af_inet- Ivp4
# SOCK_STREAM = TCP
serverSocket = socket(AF_INET, SOCK_STREAM)

# bind socket to a specific address and port
# '' means listen to all ip's
serverSocket.bind(('', serverPort))

# define at least 5 connections
serverSocket.listen(5)


# this function is executed whenever a thread is being activated
def multi_threaded_client(connectionSocket, Msgs):
    while True:
        # receiving other messages
        message = connectionSocket.recv(1024).decode()
        index = message.find(">")
        action = message[1:index - 1]
        # sending to a switch case action and other relevant info
        actions(action, message[index:-1], addr[1], addr[0])
        if action == "disconnect":
            break
    connectionSocket.close()


while True:
    # Establish the connection
    print('Ready to serve...')

    # connectionSocket is the socket after the connection has been accepted
    # addr[0]= client's ip, addr[1]= client's port
    connectionSocket, addr = serverSocket.accept()

    # checking if the port is out of bounds
    if addr[1] < 54999 or addr[1] > 55016:
        print(addr[1] + " -Not in port range")
        connectionSocket.close()

    # checking if specific port is available
    elif available_ports[addr[1]] != ("", "", 0, [str]):
        print("Chosen port is unavailable")
        connectionSocket.close()

    else:
        start_new_thread(multi_threaded_client, (connectionSocket, ))
        num_of_threads += 1

# TODO: if the user name is taken please choose another one

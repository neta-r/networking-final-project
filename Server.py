from _thread import start_new_thread
# import socket module
from socket import *
import sys  # In order to terminate the program

num_of_threads = 0

# client's Port: (is available, client's user name)
available_ports = {"55000": (False, str), "55001": (False, str), "55002": (False, str),
                   "55003": (False, str), "55004": (False, str), "55005": (False, str),
                   "55006": (False, str), "55007": (False, str), "55008": (False, str),
                   "55009": (False, str), "55010": (False, str), "55011": (False, str),
                   "55012": (False, str), "55013": (False, str), "55014": (False, str),
                   "55015": (False, str)}

# name: (ip, port, connection, [msg1, msg2,..])
users = {}


# connect to chat! In this point we already have a connection to the server
def connect(name, port, ip):
    if name not in users:
        available_ports[port][1] = name
        users[name] = (ip, port, connectionSocket, str)
        connectionSocket.send('<connected>'.encode())
        print(name + " connected")
    else:
        connectionSocket.send('<available_name>'.encode())


# message_send- is the massage according to protocol
# online_users_print- will display on the screen
def get_users():
    online_users_print = str
    online_users_send = str
    for val in users.values():
        if val[2] != 0:
            online_users_print += val[1] + ","
            online_users_send += "<" + str(val[1]) + ">"

    print(online_users_print[0:-2])
    message_send = "<users_lst><" + str(num_of_threads) + ">" + str(online_users_send) + "<end>"
    connectionSocket.send(message_send.encode())


# we need to free the port
def disconnect(port):
    available_ports[port] = (False, "")
    del users[available_ports[port][1]]
    connectionSocket.send("<disconnected>".encode())


def set_msg(rest_of_msg, port, ip):
    # rest_of_msg="name><msg>"
    index = rest_of_msg.find(">")
    name = rest_of_msg[0:index - 1]
    msg = rest_of_msg[index + 2:-1]
    if name in users:
        other_client_socket = users[name][2]
        my_name = available_ports[port][1]
        send_to_client = "<" + str(my_name) + "><" + str(msg) + ">"
        other_client_socket.send(send_to_client.encode())
        users[name][3] += "," + msg
        connectionSocket.send("<msg_sent>".encode())
    else:
        connectionSocket.send("<invalid_name>".encode())


def set_msg_all(msg, port):
    # msg = "msg>"
    my_name = available_ports[port][1]
    for key, val in users.items():
        if key is not my_name:
            other_client_socket = users[key][2]
            other_client_socket.send(msg.encode())
    connectionSocket.send("<msg_sent>".encode())


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
        "set_msg": set_msg(rest_of_msg, port, ip),
        "set_msg_all": set_msg_all(rest_of_msg, port),
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
def multi_threaded_client(connectionSocket):
    while True:
        # receiving other messages
        message = connectionSocket.recv(1024).decode()
        index = message.find(">")
        action = message[1:index - 1]
        # sending to a switch case action and other relevant info
        actions(action, message[index + 2:-1], addr[1], addr[0])
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
        connectionSocket.send("<port_out_of_range>".encode())
        connectionSocket.close()

    # # checking if specific port is available
    # elif available_ports[addr[1]][0] is True:
    #     print("Chosen port is unavailable")
    #     connectionSocket.send("<port_unavailable>".encode())
    #     connectionSocket.close()

    else:
        connectionSocket.send("<connection_established>".encode())
        available_ports[addr[1]][0] = False
        start_new_thread(multi_threaded_client, (connectionSocket,))
        num_of_threads += 1

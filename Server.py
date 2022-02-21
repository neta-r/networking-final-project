available_ports = {"55000": (str, str), "55001": (str, str), "55002": (str, str), "55003": (str, str),
                   "55004": (str, str), "55005": (str, str), "55006": (str, str), "55007": (str, str),
                   "55008": (str, str), "55009": (str, str), "55010": (str, str), "55011": (str, str),
                   "55012": (str, str), "55013": (str, str), "55014": (str, str), "55015": (str, str)}


def get_users():
    online_users_print = str
    online_users_send = str
    counter = int
    for val in available_ports.values():
        if val != ("", ""):
            counter = counter + 1
            online_users_print += val[1] + ","
            online_users_send += "<" + str(val[1]) + ">"

    print(online_users_print[0:-2])
    message_send = "<users_lst><"+counter+">"+str(online_users_send)+"<end>"
    connectionSocket.send(message_send.encode())


def disconnect():
    return "h"


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


def actions(action, rest_of_msg):
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


# "PortNum": ("IP","userName")
from re import match

# import socket module
from socket import *
import sys  # In order to terminate the program

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

# Prepare a sever socket
while True:
    # Establish the connection
    print('Ready to serve...')

    # connectionSocket is the socket after the connection has been accepted
    # addr[0]= client's ip, addr[1]= client's port
    connectionSocket, addr = serverSocket.accept()

    # checking if the port is out of bounds
    if addr[1] < 54999 or addr[1] > 55016:
        print(addr[1] + " -Not in port range")
        # Close client socket
        connectionSocket.close()

    else:
        # checking if specific port is available
        if available_ports[addr[1]] != ("", ""):
            print("Chosen port is unavailable")
            # Close client socket
            connectionSocket.close()

    try:
        connectMessage = connectionSocket.recv(1024).decode()
        # connectMassage = "<connect><name>"
        if connectMessage.rfind("<connect><", 0, 9):
            # after the >< username is writen and then >
            name = connectMessage[10:-2]
            available_ports[addr[1]] = (addr[0], name)
            connectionSocket.send('connected'.encode())
            print(name + " connected")
        else:
            connectionSocket.send('invalidMessage'.encode())

        # receiving other messages
        message = connectionSocket.recv(1024).decode()
        index = message.find(">")
        action = message[1:index - 1]
        # sending to a switch case action and other relevant info
        actions(action, message[index:-1])

        connectionSocket.close()
    except IOError:

        print("Page not found")
        # Send response message for file not found
        connectionSocket.send('HTTP/1.1 404 NOT FOUND \r\n\r\n'.encode())
        # Close client socket
        connectionSocket.close()

        serverSocket.close()
        sys.exit()  # Terminate the program after sending the corresponding data

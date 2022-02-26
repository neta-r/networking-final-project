from _thread import start_new_thread
from socket import *
import sys  # In order to terminate the program


class Server:
    # client's Port: user's name
    names = {55000: str, 55001: str, 55002: str, 55003: str, 55004: str, 55005: str,
             55006: str, 55007: str, 55008: str, 55009: str, 55010: str, 55011: str,
             55012: str, 55013: str, 55014: str, 55015: str}

    # name: [ip, port, connection, [["neta","hi"], ["reut","hi"], ["neta","how you doing"], ... "]]
    users = {}

    online_users = 0

    def __init__(self):
        # Given server port
        server_port = 50000
        # choosing type of protocol
        # af_inet- Ivp4
        # SOCK_STREAM = TCP
        server_socket = socket(AF_INET, SOCK_STREAM)

        # bind socket to a specific address and port
        # '' means listen to all ip's

        server_socket.bind(('', server_port))

        # define at least 5 connections
        server_socket.listen(5)

        print("Ready to serve!")

        while True:
            # connectionSocket is the socket after the connection has been accepted
            # addr[0]= client's ip, addr[1]= client's port
            connection_socket, addr = server_socket.accept()
            connection_socket.send("<connection_established>".encode())
            Server.online_users = int(Server.online_users)+1
            start_new_thread(Server.multi_threaded_client, (self, connection_socket, addr[0], addr[1]))

    # this function is executed whenever a thread is being activated
    def multi_threaded_client(self, connection_socket, ip, port):
        while True:
            # receiving other messages
            message = connection_socket.recv(1024).decode()
            index = message.find(">")
            action = message[1:index]
            # sending to a switch case action and other relevant info
            Server.actions(self, action, message[index + 2:-1], ip, port, connection_socket)
            if action == "disconnect":
                break
        connection_socket.close()

    # connect to chat! In this point we already have a connection to the server
    def connect(self, name, port, ip, connection_socket):
        if name not in Server.users:
            Server.names[port] = name
            Server.users[name] = [ip, port, connection_socket, ""]
            connection_socket.send('<connected>'.encode())
            print(name + " connected")
        else:
            connection_socket.send('<available_name>'.encode())

    # message_send- is the massage according to protocol
    # online_users_print- will display on the screen
    def get_users(self, connection_socket):
        online_users_print = ""
        online_users_send = ""
        for key, val in Server.users.items():
            if val[2] != 0:
                online_users_print = online_users_print + str(key) + ","
                online_users_send = online_users_send + "<" + str(key) + ">"

        print("online users: " + online_users_print[0:-1])
        message_send = "<users_lst><" + str(Server.online_users) + ">" + str(online_users_send) + "<end>"
        connection_socket.send(message_send.encode())

    # we need to free the port
    def disconnect(self, port, connection_socket):
        Server.online_users = int(Server.online_users) - 1
        name = Server.names[port]
        Server.users.pop(Server.names[port])
        # del users[names[port]]
        Server.names[port] = str
        connection_socket.send("<disconnected>".encode())
        print(name + ' left chat')

    def set_msg(self, rest_of_msg, port, ip, connection_socket):
        my_name = Server.names[port]
        # rest_of_msg="name><msg>"
        index = rest_of_msg.find(">")
        name = rest_of_msg[0:index]
        msg = rest_of_msg[index + 2:]
        # if name == my_name:
        #     connectionSocket.send("<message_to_yourself>".encode())
        # else:
        if name in Server.users:
            other_client_socket = Server.users[name][2]
            send_to_client = "<msg><" + str(my_name) + "><" + str(msg) + ">"
            other_client_socket.send(send_to_client.encode())
            Server.users[name][3] += my_name + ":" + msg + "\n"
            connection_socket.send("<msg_sent>".encode())
        else:
            connection_socket.send("<invalid_name>".encode())

    def set_msg_all(self, msg, port, connection_socket):
        # msg = "msg>"
        my_name = Server.names[port]
        for key, val in Server.users.items():
            # if key is not my_name:
            other_client_socket = Server.users[key][2]
            Server.users[key][3] += my_name + ":" + msg + "\n"
            other_client_socket.send(("<msg>" + msg).encode())
        connection_socket.send("<msg_sent>".encode())

    def show_all_msg(self, port, connection_socket):
        # TODO: לשנות את ההפרדה לדיקשנרי
        # TODO: לוודא ביצוע פעולות עבור משתמשים שהתחברו מאוחר יותר (טרדים)
        my_name = Server.names[port]
        msgs = Server.users[my_name][3]
        if msgs != "":
            msgs_and_users = msgs.split('\n')
            num_of_msgs = len(msgs_and_users) - 1
            send = "<msg_lst><" + str(num_of_msgs) + ">"
            for arr in msgs_and_users:
                if arr != "":
                    user_name, user_msg = arr.split(':')
                    send += "<" + user_name + ":" + user_msg + ">"
            send += "<end>"
            connection_socket.send(send.encode())
        else:
            connection_socket.send("<no_msgs>".encode())

    def get_list_file(self, connection_socket):
        return "h"

    def download(self, connection_socket):
        return "h"

    def proceed(self, connection_socket):
        return "h"

    def actions(self, action, rest_of_msg, port, ip, connection_socket):
        if action == "connect":
            Server.connect(self, rest_of_msg, port, ip, connection_socket)
        elif action == "get_users":
            Server.get_users(self, connection_socket)
        elif action == "disconnect":
            Server.disconnect(self, port, connection_socket)
        elif action == "set_msg":
            Server.set_msg(self, rest_of_msg, port, ip, connection_socket)
        elif action == "set_msg_all":
            print(connection_socket)
            Server.set_msg_all(self, rest_of_msg, port, connection_socket)
        elif action == "show_all_msgs":
            Server.show_all_msg(self, port, connection_socket)
        elif action == "get_list_file":
            Server.get_list_file(self, connection_socket)
        elif action == "download":
            Server.download(self, connection_socket)
        elif action == "proceed":
            Server.proceed(self, connection_socket)
        else:
            return "Invalid action"


if __name__ == '__main__':
    server = Server()

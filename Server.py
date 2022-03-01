import os
import pickle
import time
import timeit
from _thread import start_new_thread
import sys  # In order to terminate the program
from socket import *


class Chunk(object):
    def __init__(self):
        self.checksum = 0
        self.data = ""
        self.NAck = False


class Server:
    # Given server port

    server_port = 50000
    # choosing type of protocol
    # af_inet- Ivp4
    # SOCK_STREAM = TCP
    server_socket_TCP = socket(AF_INET, SOCK_STREAM)

    # SOCK_DGRAM = UDP
    server_socket_UDP = socket(AF_INET, SOCK_DGRAM)

    # client's Port: user's name
    names = {55000: str, 55001: str, 55002: str, 55003: str, 55004: str, 55005: str,
             55006: str, 55007: str, 55008: str, 55009: str, 55010: str, 55011: str,
             55012: str, 55013: str, 55014: str, 55015: str}

    # name: [ip, port, tcp_connection, [["neta","hi"], ["reut","hi"], ["neta","how you doing"], ... "]]
    users = {}
    packet = {}
    online_users = 0

    def __init__(self):

        # bind socket to a specific address and port
        # '' means listen to all ip's
        self.server_socket_TCP.bind(('', self.server_port))

        # define at least 5 connections
        self.server_socket_TCP.listen(5)

        print("Ready to serve!")

        while True:
            # connectionSocket is the socket after the connection has been accepted
            # addr[0]= client's ip, addr[1]= client's port
            connection_socket, addr = self.server_socket_TCP.accept()
            connection_socket.send("<connection_established>".encode())
            Server.online_users = int(Server.online_users) + 1
            start_new_thread(Server.multi_threaded_client, (self, connection_socket, addr[0], addr[1]))

    # this function is executed whenever a thread is being activated
    def multi_threaded_client(self, connection_socket, ip, port):
        while True:
            # receiving other messages
            message = connection_socket.recv(1024).decode()
            index = message.find(">")
            action = message[1:index]
            # sending to a switch case action and other relevant info
            Server.actions(self, action, message[index + 2:-1], port, ip, connection_socket)
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
            other_client_socket.send(("<msg><" + my_name + "><" + msg + ">").encode())
        connection_socket.send("<msg_sent>".encode())

    def get_list_file(self, connection_socket):
        cwd = os.getcwd()
        only_files = [os.path.join(cwd, f) for f in os.listdir(cwd) if
                      os.path.isfile(os.path.join(cwd, f))]
        files = "<file_lst>"
        for file in only_files:
            files = files + "<" + file + ">"
            # print(file + "\n")
        files = files + "<end>"
        connection_socket.send(files.encode())

    # TODO: Find checksum for each chunk
    def checksum(self, chunk):
        pass

    def send_file(self, server_socket_UDP, ip, file_name, port, file_bytes):
        with open(file_name, 'rb') as f:
            print("in send file 1")
            # check if the client received file size - ACK, if not server resend it again after 10 sec
            server_socket_UDP.settimeout(100)
            while True:
                try:
                    # send file size to client
                    # server_socket_UDP.sendto("HIIII".encode(), (ip, port))
                    server_socket_UDP.sendto(("<download>" + str(file_bytes)).encode(), (ip, port))
                    ACK, address = server_socket_UDP.recvfrom(1024)
                    print(ACK)
                    break
                except Exception as e:
                    server_socket_UDP.sendto(("<download>" + str(file_bytes)).encode(), (ip, port))

            # divide data to chunks
            data = f.read(1024)
            while data:
                chunk = Chunk()
                chunk.data = data
                chunk.checksum = self.checksum(chunk.data)
                chunk_in_binary = pickle.dumps(chunk)  # serialize chunk into bytes
                flag = True
                while flag:
                    flag = False
                    try:
                        server_socket_UDP.sendto(chunk_in_binary, (ip, port))
                        ACK, address = server_socket_UDP.recvfrom(2048)
                        print(ACK)
                        break
                    except Exception as e:
                        flag = True
                data = f.read(2048)

    # Download - UDP
    def download(self, connection_socket, ip, file_name, port):
        # Bytes num of file
        file_bytes = os.path.getsize(file_name)

        # TODO: CHECK 64after send to
        # after send file
        if file_bytes >= (1 << 64):
            connection_socket.send('<too_big>'.encode())
            return

        # opening UDP connection
        self.server_socket_UDP.bind(('', self.server_port))
        # print("The server is ready to receive...")
        # message, clientAddress = self.server_socket_UDP.recvfrom(2048)
        # print("Get from client:", message)
        # modifiedMessage = message.upper()
        self.send_file(self.server_socket_UDP, ip, file_name, port, file_bytes)
        # self.server_socket_UDP.sendto(modifiedMessage, clientAddress)
        self.server_socket_UDP.close()

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
        elif action == "get_list_file":
            Server.get_list_file(self, connection_socket)
        elif action == "download":
            Server.download(self, connection_socket, ip, rest_of_msg, port)
        elif action == "proceed":
            Server.proceed(self, connection_socket)
        else:
            return "Invalid action"


if __name__ == '__main__':
    server = Server()

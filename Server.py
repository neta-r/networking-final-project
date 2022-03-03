import os
import pickle
import math
import time
import timeit
import threading
import sys  # In order to terminate the program
from socket import *
import hashlib


class Chunk(object):
    def __init__(self):
        self.checksum = 0
        self.data = ""


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

    # name: [ip, port, tcp_connection]
    users = {}
    packet = {}
    online_users = 0
    # file_name = (size, [user1,user2,..])
    files = {}

    def __init__(self):
        self.server_socket_TCP.bind(('', self.server_port))
        self.server_socket_UDP.bind(('', self.server_port))

        # define at least 5 connections
        self.server_socket_TCP.listen(5)

        print("Ready to serve!")

        while True:
            # connectionSocket is the socket after the connection has been accepted
            # addr[0]= client's ip, addr[1]= client's port
            connection_socket, addr = self.server_socket_TCP.accept()
            connection_socket.send("<connection_established>".encode())
            Server.online_users = int(Server.online_users) + 1
            t = threading.Thread(target=Server.multi_threaded_client, args=(self, connection_socket, addr[0], addr[1]))
            t.start()

    # this function is executed whenever a thread is being activated - listens to tcp messages
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
            connection_socket.send('<connected_to_chat>'.encode())
            print(name + " connected")
        else:
            connection_socket.send('<name_taken>'.encode())

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

    def get_list_file(self, connection_socket):
        cwd = os.getcwd()
        for f in os.listdir(cwd):
            if os.path.isfile(os.path.join(cwd, f)) and f not in self.files:
                self.files[os.path.join(cwd, f)] = (os.path.getsize(f), [])

        files = "<file_lst>"
        for file in self.files:
            files = files + "<" + file + ">"
        files = files + "<end>"
        connection_socket.send(files.encode())

    def checksum(self, chunk_data):
        md5_hash = hashlib.md5()
        md5_hash.update(chunk_data)
        digest = md5_hash.hexdigest()
        return digest

    def send_and_ack(self, binary_msg, ip, port):
        self.server_socket_UDP.settimeout(100)
        # check if the client received msg - ACK, if not server resend it when timeout exception is being raised
        while True:
            try:
                # send file size to client
                self.server_socket_UDP.sendto(binary_msg, (ip, port))
                ACK, address = self.server_socket_UDP.recvfrom(1024)
                print(ACK)
                break
            except Exception:
                self.server_socket_UDP.sendto(binary_msg, (ip, port))

    def send_file(self, ip, file_name, port, file_bytes):
        # <first><file_size - [:1/2]>nvnvnvn<second><file_size[1/2:]>jfbvkjsbfl
        with open(file_name, 'rb') as f:
            msg = str(file_bytes).encode()
            self.send_and_ack(msg, ip, port)
            left_to_send = file_bytes
            while left_to_send > 0:
                if left_to_send > 1024:
                    # divide data to chunks
                    data = f.read(1024)
                    left_to_send -= 1024
                else:
                    data = f.read(left_to_send)
                    left_to_send = 0
                chunk = Chunk()
                chunk.data = data
                chunk.checksum = self.checksum(chunk.data)
                chunk_in_binary = pickle.dumps(chunk)  # serialize chunk into bytes
                self.send_and_ack(chunk_in_binary, ip, port)

    # Download - UDP
    def download(self, connection_socket, ip, file_name, port):
        # turning short name to full name
        for f in self.files:
            if f.__contains__(file_name):
                file_name = f
        # Bytes num of file
        file_bytes = self.files[file_name][0]
        # 65536 bytes = 64 kb
        # 1024 byte = 1 kb
        if file_bytes >= 65536:
            connection_socket.send('<too_big>'.encode())
            return
        # adding client's name to files list
        clients_name = self.names[port]
        self.files[file_name][1].append(clients_name)
        print(str(self.files[file_name][1]))

        # sending the client a signal to enter his receiving file function
        self.send_and_ack("<first>".encode(), ip, port)
        # sending client half of the file (rounded down)
        self.send_file(ip, file_name, port, round(file_bytes / 2))

    def proceed(self, ip, port):
        file_name = ""
        clients_name = self.names[port]

        # finding file user want to proceed downloading
        for file, val in self.files.items():
            if clients_name in val[1]:
                file_name = file
                break

        # checking if client pressed download before pressing proceed
        if len(file_name) == 0:
            self.send_and_ack("<press_download_first>".encode(), ip, port)

        file_bytes = self.files[file_name][0]

        # sending the client a signal to enter his receiving file function
        self.send_and_ack("<second>".encode(), ip, port)
        # sending client half of the file (rounded up)
        self.send_file(ip, file_name, port, int(math.ceil(file_bytes / 2)))
        self.files[file_name][1].remove(clients_name)

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
            Server.proceed(self, ip, port)
        else:
            return "Invalid action"


if __name__ == '__main__':
    server = Server()

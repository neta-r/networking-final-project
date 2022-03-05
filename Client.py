import hashlib
import os
import pickle
import time
import threading
from socket import *

# from tkinter import *
from Server import Chunk


class Client:
    name = str
    port = int
    server_name = '127.0.0.1'
    SERVER_ADDRESS = (server_name, 50000)
    dir_files = []
    flag = False
    isAlive = True
    output = ""

    def __init__(self):
        self.get_port()
        self.t1 = threading.Thread(target=Client.actions, args=(self,))
        self.t2 = threading.Thread(target=Client.receive_msgs, args=(self,))
        self.t3 = threading.Thread(target=Client.receive_udp_msgs, args=(self,))
        self.t1.daemon = True
        self.t2.daemon = True
        self.t3.daemon = True
        self.t2.start()
        self.t3.start()
        while True:
            self.name = input("Input username: ")
            connect_request = "<connect><" + self.name + ">"
            # clientSocket.send(bytes(sentence, encoding="UTF-8"))
            self.client_socket_TCP.send(connect_request.encode())
            time.sleep(2)
            if self.flag:
                break
        Client.menu(self)
        # time.sleep(3)
        self.t1.start()

    def print_and_output(self, msg):
        print(msg)
        self.output = self.output + msg

    def get_port(self):
        while True:
            client_input = input("Enter port number between 55000 to 55015: ")
            # checking if input is a number
            try:
                self.port = int(client_input)
                # checking if the port is out of bounds
                if 55000 <= self.port <= 55016:
                    # checking if specific port is available
                    try:
                        self.client_socket_TCP = socket(AF_INET, SOCK_STREAM)
                        self.client_socket_TCP.bind((self.server_name, self.port))
                        self.client_socket_UDP = socket(AF_INET, SOCK_DGRAM)
                        self.client_socket_UDP.bind((self.server_name, self.port))
                        self.client_socket_TCP.connect(self.SERVER_ADDRESS)
                        break
                    except OSError as e:
                        # error number 10048 = Port is taken,
                        # Only one usage of each socket address is normally permitted
                        if e.errno == 10048:
                            self.print_and_output("Port is unavailable, Please try another one!")
                else:
                    self.print_and_output("Port out of range!\n")
            except ValueError:
                self.print_and_output("Please enter numeric value!\n")

    def get_users(self):
        self.client_socket_TCP.send("<get_users>".encode())

    def disconnect(self):
        self.client_socket_TCP.send("<disconnect>".encode())

    def set_msg(self):
        other_user = input("Input username: ")
        msg = input("Input message: ")
        set_msg_request = "<set_msg><" + other_user + "><" + msg + ">"
        self.client_socket_TCP.send(set_msg_request.encode())

    def set_msg_all(self):
        msg = input("Input message: ")
        set_msg_all_request = "<set_msg_all><" + msg + ">"
        self.client_socket_TCP.send(set_msg_all_request.encode())

    def get_list_file(self):
        self.client_socket_TCP.send("<get_list_file>".encode())

    # checking if name is valid and if it is the long name, returns the short name
    def is_valid(self, file_name):
        for f in self.dir_files:
            # windows -
            if file_name.__contains__(f) and not f.__contains__("/"):
                # if file_name.__contains__(f) and not f.__contains__("\\"):
                return f
        return ''

    # Download - TCP
    def download(self):
        # Make sure client saw file list
        self.get_list_file()
        time.sleep(3)
        choose_file = input("Please enter requested file name: ")
        choose_file = self.is_valid(choose_file)
        # invalid name
        if not len(choose_file) > 0:
            while True:
                self.print_and_output("Invalid name\n")
                choose_file = input("Please enter requested file name or 'q' to quit: ")
                if choose_file == 'q':
                    return
                # if user chose the long name we'll find the short name and send it
                choose_file = self.is_valid(choose_file)
                if len(choose_file):
                    break

        # format - <download><file_name>
        self.client_socket_TCP.send(("<download><" + choose_file + ">").encode())

    def proceed(self):
        self.client_socket_TCP.sendto("<proceed>".encode(), self.SERVER_ADDRESS)

    def switcher(self, action):
        if action == 1:
            Client.get_users(self)
        elif action == 2:
            Client.disconnect(self)
        elif action == 3:
            Client.set_msg(self)
        elif action == 4:
            Client.set_msg_all(self)
        elif action == 5:
            Client.get_list_file(self)
        elif action == 6:
            Client.download(self)
        elif action == 7:
            Client.proceed(self)
        else:
            return "Invalid action"

    def menu(self):
        self.print_and_output("Action menu: \n")
        self.print_and_output("1- get users list\n")
        self.print_and_output("2- disconnect\n")
        self.print_and_output("3- send private message\n")
        self.print_and_output("4- send message to all online users\n")
        self.print_and_output("5- get list of files\n")
        self.print_and_output("6- download file\n")
        self.print_and_output("7- proceed\n")

    def checksum(self, chunk_data):
        md5_hash = hashlib.md5()
        md5_hash.update(chunk_data)
        digest = md5_hash.hexdigest()
        return digest

    def receive_half_file(self):
        # receiving file size
        message, serverAddress = self.client_socket_UDP.recvfrom(2048)
        file_size = float(message.decode())
        self.client_socket_UDP.sendto("ACK".encode(), serverAddress)

        count_bytes = 0
        count_packets = 1
        while True:
            bytes_read = self.client_socket_UDP.recv(2048)
            # trying to decode if bytes_read are string - "stop"
            try:
                dec = bytes_read.decode()
                if dec == "stop":
                    self.client_socket_UDP.sendto("ACK".encode(), serverAddress)
                    break
            # else - bytes_read are bytes , we need to load them
            except:
                data_read = pickle.loads(bytes_read)
                receive_checksum = self.checksum(data_read.data)
                if receive_checksum == data_read.checksum:
                    # illustration of 50% packet loss
                    # if count_packets % 2 == 0:
                    #     time.sleep(2)
                    self.client_socket_UDP.sendto("ACK".encode(), serverAddress)
                    count_bytes = count_bytes + len(data_read.data)
                    count_packets = count_packets + 1
        return file_size

    def receive_udp_msgs(self):
        while True:
            message, serverAddress = self.client_socket_UDP.recvfrom(2048)
            if message:
                if message.startswith("<press_download_first>".encode()):
                    self.client_socket_UDP.sendto("ACK".encode(), serverAddress)
                    self.print_and_output("You can't proceed because you are not downloading anything now\n")
                elif message.startswith("<first>".encode()):
                    # sending server ack on "<first>" msg
                    self.client_socket_UDP.sendto("ACK".encode(), serverAddress)
                    file_size = self.receive_half_file()
                    self.print_and_output(
                        "User " + self.name + " downloaded 50% out of file. Last byte is: " + str(file_size))
                elif message.startswith("<second>".encode()):
                    self.client_socket_UDP.sendto("ACK".encode(), serverAddress)
                    file_size = self.receive_half_file()
                    self.print_and_output("User " + self.name + " downloaded 100% out of file. Last byte is: " +
                                          str(file_size * 2))

    def receive_msgs(self):
        while True:
            buffer = self.client_socket_TCP.recv(1024)
            if buffer:
                message = buffer.decode()
                # get users
                if message.startswith("<users_lst>"):
                    message = message[12:]
                    # server_feedback = "num_of_users><user1><user2>...<end>
                    index = message.find(">")
                    num_of_usr = message[0:index]
                    self.print_and_output("Number of users connected: " + num_of_usr + "\nThe users are: ")
                    message = message[index + 1:]
                    # server_feedback = "<usr1><usr2>...<end>
                    stringUser = ""
                    for _ in range(int(num_of_usr)):
                        index = message.find(">")
                        user = message[1:index]
                        stringUser = stringUser + user + ", "
                        message = message[index + 1:]
                    self.print_and_output(stringUser[0:-2])

                # connect to socket
                elif message == "<connection_established>":
                    self.print_and_output("connection established\n")

                # connected to chat
                elif message == "<connected_to_chat>":
                    self.flag = True
                    time.sleep(1)
                    self.print_and_output("Thank you!\n")

                elif message == "<name_taken>":
                    self.flag = False
                    self.print_and_output("name is already taken!\n")

                # disconnect
                elif message.startswith("<disconnected>"):
                    self.print_and_output("Successfully disconnected\n")
                    self.client_socket_TCP.close()
                    self.client_socket_UDP.close()
                    self.isAlive = False
                    exit(0)

                # send message
                elif message.startswith("<message_to_yourself>"):
                    self.print_and_output("You can't send a message to yourself\n")

                elif message.startswith("<invalid_name>"):
                    self.print_and_output("The name you chose is not in the chatroom!\n")

                # show all messages
                elif message.startswith("<no_msgs>"):
                    self.print_and_output("You have no messages yet\n")

                elif message.startswith("<msg>"):
                    message = message[6:]
                    index = message.find(">")
                    name = message[0:index]
                    msg = message[index + 2:-1]
                    self.print_and_output("\n" + name + ": " + msg)

                # list_file
                elif message.startswith("<file_lst>"):
                    message = message[11:]
                    self.print_and_output("files: \n")
                    while not message.startswith("end"):
                        index = message.find(">")
                        file = message[0:index]
                        if file not in self.dir_files:
                            self.dir_files.append(file)
                            self.print_and_output(file + "\n")
                            # windows -
                            index1 = file.rfind("/")
                            # index1 = file.rfind("\\")
                            self.dir_files.append(file[index1 + 1:])
                        message = message[index + 2:]
                elif message.startswith("<too_big>"):
                    self.print_and_output("The chosen file bis too large\n")

    def actions(self):
        while True:
            time.sleep(3)
            if self.isAlive:
                client_input = input("Please select action: \n")
                # checking if input is a number
                try:
                    action = int(client_input)
                    if int(action) < 1 or int(action) > 7:
                        self.print_and_output("Please choose number between 1 to 7\n")
                    else:
                        Client.switcher(self, action)
                except ValueError:
                    self.print_and_output("Please enter numeric value!\n")


if __name__ == '__main__':
    client = Client()
    # for clean disconnect
    while client.isAlive:
        continue
    exit(0)

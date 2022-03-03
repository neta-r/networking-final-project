import hashlib
import os
import pickle
import time
import threading
from socket import *
from tkinter import *
from Server import Chunk


#
# def rgb_hack(rgb):
#     return "#%02x%02x%02x" % rgb


class Client:
    client_socket_TCP = SocketKind
    client_socket_UDP = SocketKind
    name = str
    port = int
    server_name = '192.168.1.36'
    SERVER_ADDRESS = (server_name, 50000)
    dir_files = []

    def __init__(self):
        # window = Tk()
        # window.title("Login")
        # window.geometry("400x300")
        # window.config(bg='#EEBAC6')

        # welcome_Label = Label(window, text=" Welcome to our chat! ", fg='pink', bg='white', relief=GROOVE,
        #                       font=("arial", 12, "bold"))
        # welcome_Label.place(relx=0.5, rely=0.1, anchor=CENTER)
        #
        # insert_port_label = Label(window, text="Port Number: ", fg='white', bg='#EEBAC6', relief=FLAT,
        #                           font=("arial", 12, "bold"))
        # insert_port_label.place(relx=0.05, rely=0.3, anchor=W)
        #
        # port_entry = Entry(window, bd=5)
        # port_entry.pack(side=RIGHT)
        #
        # insert_username_label = Label(window, text="User Name: ", fg='white', bg='#EEBAC6', relief=FLAT,
        #                               font=("arial", 12, "bold"))
        # insert_username_label.place(relx=0.05, rely=0.5, anchor=W)
        #
        # username_entry = Entry(window, bd=5)
        # username_entry.pack(side=RIGHT)
        #
        # sign_in_button = Button(window, text="Sign In", fg='white', bg='pink', relief=RIDGE, font=("arial", 12, "bold"))
        # sign_in_button.place(x=165, y=230)
        # window.mainloop()

        self.get_port()
        while True:
            self.name = input("Input username: ")
            connect_request = "<connect><" + self.name + ">"
            # clientSocket.send(bytes(sentence, encoding="UTF-8"))
            self.client_socket_TCP.send(connect_request.encode())
            self.client_socket_TCP.send("<get_list_file>".encode())
            time.sleep(2)
            print("Thank you!\n")
            break
        Client.menu(self)
        t1 = threading.Thread(target=Client.actions, args=(self,))
        t2 = threading.Thread(target=Client.receive_msgs, args=(self,))
        t3 = threading.Thread(target=Client.receive_udp_msgs, args=(self,))
        t2.start()
        t3.start()
        t1.start()

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
                        self.client_socket_TCP.bind(('192.168.1.36', self.port))
                        self.client_socket_UDP = socket(AF_INET, SOCK_DGRAM)
                        self.client_socket_UDP.bind(('192.168.1.36', self.port))
                        self.client_socket_TCP.connect(self.SERVER_ADDRESS)
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

    def get_users(self):
        self.client_socket_TCP.send("<get_users>".encode())

    def disconnect(self):
        self.client_socket_TCP.send("<disconnect>".encode())
        exit()

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
        # TODO: להעיף
        self.client_socket_TCP.send("<get_list_file>".encode())
        time.sleep(2)
        for f in self.dir_files:
            if f.__contains__("\\"):
                print(f + "\n")

    # checking if name is valid and if it is the long name, returns the short name
    def is_valid(self, file_name):
        for f in self.dir_files:
            if file_name.__contains__(f) and not f.__contains__("\\"):
                return f
        return ''

    # Download - TCP
    def download(self):
        # Make sure client saw file list
        print("This are your available files:\n")
        self.get_list_file()
        choose_file = input("Please enter requested file name: ")
        choose_file = self.is_valid(choose_file)
        # invalid name
        if not len(choose_file) > 0:
            while True:
                print("Invalid name\n")
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
        self.client_socket_UDP.sendto("<proceed>".encode(), self.SERVER_ADDRESS)

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
        print("Action menu: \n")
        print("1- get users list\n")
        print("2- disconnect\n")
        print("3- send private message\n")
        print("4- send message to all online users\n")
        print("5- get list of files\n")
        print("6- download file\n")
        print("7- proceed\n")

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
        while True:
            bytes_read = self.client_socket_UDP.recv(2048)
            data_read = pickle.loads(bytes_read)
            # print(data_read.data)
            receive_checksum = self.checksum(data_read.data)
            if receive_checksum == data_read.checksum:
                self.client_socket_UDP.sendto("ACK".encode(), serverAddress)
                count_bytes = count_bytes + len(data_read.data)
            if count_bytes >= file_size:
                break
        return file_size

    def receive_udp_msgs(self):
        while True:
            message, serverAddress = self.client_socket_UDP.recvfrom(2048)
            if message:
                if message.startswith("<press_download_first>".encode()):
                    print("You can't proceed because you are not downloading anything\n")
                if message.startswith("<first>".encode()):
                    # sending server ack on "<first>" msg
                    self.client_socket_UDP.sendto("ACK".encode(), serverAddress)
                    file_size = self.receive_half_file()
                    print("User " + self.name + " downloaded 50% out of file. Last byte is: " + str(file_size))
                if message.startswith("<second>".encode()):
                    self.client_socket_UDP.sendto("ACK".encode(), serverAddress)
                    file_size = self.receive_half_file()
                    print("User " + self.name + " downloaded 100% out of file. Last byte is: " +
                        str(file_size) * 2)

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
                    print("Number of users connected: " + num_of_usr + "\nThe users are: ")
                    message = message[index + 1:]
                    # server_feedback = "<usr1><usr2>...<end>
                    stringUser = ""
                    for _ in range(int(num_of_usr)):
                        index = message.find(">")
                        user = message[1:index]
                        stringUser = stringUser + user + ", "
                        message = message[index + 1:]
                    print(stringUser[0:-2])

                # connect
                elif message == "<connection_established>":
                    print("connection established\n")

                # disconnect
                elif message.startswith("<disconnected>"):
                    print("Successfully disconnected\n")
                    self.client_socket_TCP.close()
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

                elif message.startswith("<msg>"):
                    message = message[6:]
                    index = message.find(">")
                    name = message[0:index]
                    msg = message[index + 2:-1]
                    print("\n" + name + ": " + msg)

                # list_file
                elif message.startswith("<file_lst>"):
                    message = message[11:]
                    while not message.startswith("end"):
                        index = message.find(">")
                        file = message[0:index]
                        self.dir_files.append(file)
                        index1 = file.rfind("\\")
                        self.dir_files.append(file[index1 + 1:])
                        message = message[index + 2:]
                elif message.startswith("<too_big>"):
                    print("The chosen file bis too large\n")

    def actions(self):
        self.client_socket_TCP.send("<get_list_file>".encode())
        while True:
            time.sleep(1)
            client_input = input("Please select action: \n")
            # checking if input is a number
            try:
                action = int(client_input)
                if int(action) < 1 or int(action) > 7:
                    print("Please choose number between 1 to 7\n")
                else:
                    Client.switcher(self, action)
            except ValueError:
                print("Please enter numeric value!\n")


if __name__ == '__main__':
    client = Client()

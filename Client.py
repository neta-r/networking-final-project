import time
import threading
from socket import *
from Server import Server

class Client:
    client_socket = SocketKind
    name = str
    port = int

    def __init__(self):
        self.get_port()
        while True:
            self.name = input("Input username: ")
            connect_request = "<connect><" + self.name + ">"
            # clientSocket.send(bytes(sentence, encoding="UTF-8"))
            self.client_socket.send(connect_request.encode())
            print("Thank you!\n")
            break
        Client.menu(self)
        t1 = threading.Thread(target=Client.actions, args=(self,))
        t2 = threading.Thread(target=Client.receive_msgs, args=(self,))
        t2.start()
        t1.start()

    def get_port(self):
        server_name = '127.0.0.1'
        while True:
            client_input = input("Enter port number between 55000 to 55015: ")
            # checking if input is a number
            try:
                self.port = int(client_input)
                # checking if the port is out of bounds
                if 55000 <= self.port <= 55016:
                    # checking if specific port is available
                    try:
                        SERVER_ADDRESS = (server_name, 50000)
                        self.client_socket = socket(AF_INET, SOCK_STREAM)
                        self.client_socket.bind(('0.0.0.0', self.port))
                        self.client_socket.connect(SERVER_ADDRESS)
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
        self.client_socket.send("<get_users>".encode())

    def disconnect(self):
        self.client_socket.send("<disconnect>".encode())
        exit()

    def set_msg(self):
        other_user = input("Input username: ")
        msg = input("Input message: ")
        set_msg_request = "<set_msg><" + other_user + "><" + msg + ">"
        self.client_socket.send(set_msg_request.encode())

    def set_msg_all(self):
        msg = input("Input message: ")
        set_msg_all_request = "<set_msg_all><" + msg + ">"
        self.client_socket.send(set_msg_all_request.encode())


    def show_all_msg(self):
        self.client_socket.send("<show_all_msgs>".encode())

    def get_list_file(self):
        return "h"

    def download(self):
        return "h"

    def proceed(self):
        return "h"

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
            Client.show_all_msg(self)
        elif action == 6:
            Client.get_list_file(self)
        elif action == 7:
            Client.download(self)
        elif action == 8:
            Client.proceed(self)
        else:
            return "Invalid action"

    def menu(self):
        print("Action menu: \n")
        print("1- get users list\n")
        print("2- disconnect\n")
        print("3- send private message\n")
        print("4- send message to all online users\n")
        print("5- show all messages\n")
        print("6- get list of files\n")
        print("7- download file\n")
        print("8- proceed\n")

    def receive_msgs(self):
        while True:
            # message="<name><msg>"
            buffer = self.client_socket.recv(1024)
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
                    self.client_socket.close()
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

                elif message.startswith("<msg_lst>"):
                    message = message[10:]
                    # message = "num_of_msgs><msg1><msg2>...<end>"
                    index = message.find(">")
                    num_of_msgs = message[0:index]
                    print("Number of messages: " + num_of_msgs + "\nThe messages are:")
                    message = message[index + 1:]
                    # message = "<msg1><msg2>...<end>
                    for _ in range(int(num_of_msgs)):
                        index = message.find(">")
                        msg = message[1:index]
                        print(msg + ", ")
                        message = message[index + 1:]
                # else:
                    # print(message)

    def actions(self):
        while True:
            time.sleep(2)
            client_input = input("Please select action: \n")
            # checking if input is a number
            try:
                action = int(client_input)
                if int(action) < 1 or int(action) > 8:
                    print("Please choose number between 1 to 8\n")
                else:
                    Client.switcher(self, action)
            except ValueError:
                print("Please enter numeric value!\n")


if __name__ == '__main__':
    client = Client()


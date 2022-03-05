import threading
import time
import unittest
from unittest import mock
from unittest.mock import patch, Mock

from Client import Client
from Server import Server


def create_server():
    Server()


def test_scenario(side_effect, yes_message, no_message=None):
    try:
        with mock.patch('builtins.input', side_effect=side_effect):
            client = Client()
            while True:
                if client.isAlive:
                    continue
                else:
                    assert client.output.__contains__(yes_message)
                    if no_message is not None:
                        assert not client.output.__contains__(no_message)
                    break
    except Exception:
        return


# creating a server to connect to
t1 = threading.Thread(target=create_server)
t1.daemon = True


class test_port(unittest.TestCase):
    def test(self):
        t1.start()

        print("\n---------------------DISCONNECTED TEST---------------------\n\n")
        test_scenario(['55000', 'amit', '2'], "Successfully disconnected", "Port out of range!")
        time.sleep(5)

        print("\n---------------------GET USERS LIST TEST---------------------\n\n")
        test_scenario(['55001', 'amit', '1', '2'], "The users are: \namit")

        time.sleep(5)
        print("\n---------------------SEND PRIVATE MESSAGE TEST---------------------\n\n")
        test_scenario(['55002', 'amit', '3', 'amit', 'hi', '2'], "amit: hi")

        time.sleep(5)
        print("\n---------------------SEND PUBLIC MESSAGE TEST---------------------\n\n")
        test_scenario(['55003', 'amit', '4', 'hi', '2'], "amit: hi")

        time.sleep(5)
        print("\n---------------------GET FILES LIST TES---------------------\n\n")
        test_scenario(['55004', 'amit', '5', '2'], "files: \n")

        time.sleep(5)
        print("\n---------------------DOWNLOAD TEST---------------------\n\n")
        test_scenario(['55005', 'amit', '6', 'test.log', '2'], "User amit downloaded 50% out of file. Last byte is: ")

        time.sleep(5)
        print("\n---------------------PROCEED TEST---------------------\n\n")
        test_scenario(['55006',
        'amit', '6', 'test.log', '7', '2'], "User amit downloaded 100% out of file. Last byte is: ")

        print("\n----------------------------INVALID ACTION----------------------------\n\n")

        print("\n---------------------INVALID PROCEED TEST---------------------\n\n")
        test_scenario(['55007', 'amit', '7', '2'], "You can't proceed because you are not downloading anything now")
        time.sleep(5)

        print("\n---------------------INVALID PORT NUMBER TEST---------------------\n\n")
        test_scenario(['55030', '55008', 'amit', '2'], "Port out of range!")
        time.sleep(5)

        print("\n---------------------INVALID PORT NUMBER TEST---------------------\n\n")
        test_scenario(['hi', '55009', 'amit', '2'], "Please enter numeric value!")
        time.sleep(5)

        print("\n---------------------INVALID ACTION NUMBER TEST---------------------\n\n")
        test_scenario(['55010', 'amit', '9', '2'], "Please choose number between 1 to 7")
        time.sleep(5)

        print("\n---------------------INVALID ACTION NUMBER TEST---------------------\n\n")
        test_scenario(['55011', 'amit', 'hi', '2'], "Please enter numeric value!")
        time.sleep(5)

        print("\n-----------------INVALID USER TEST------------------\n\n")
        test_scenario(['550012', 'amit', '3', 'neta', 'hi', '2'], "The name you chose is not in the chatroom!")
        time.sleep(5)

        print("\n-----------------INVALID FILE NAME TEST------------------\n\n")
        test_scenario(['55013', 'amit', '6', 'Hello.txt', 'q', '2'], "Invalid name")

        print("\n----------------- TESTS PASSED!!! (: ------------------\n\n")

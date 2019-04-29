import socket
import sys
import time
import argparse
import threading

class _Node_Handler: #Kinda unncessary. Just left it there
    def __init__(self):
        pass

    def listen_and_connect_available_node(self):
        pass

    def _connect_node(self, node_name):
        pass

    def _kill_node(self, node_name):
        pass

class _Pub_Sub_Handler:

    def __init__(self, device_connection = None, pub_port = None, sub_port = None):

        if device_connection is None:
            device_connection = "tcp://127.0.0.101" #Different from mechos, because we might be using udp as well
        if pub_port is None:
            pub_port = "5559"
        if sub_port is None:
            sub_port = "5560"

        self.device_connection = device_connection
        self.pub_port = pub_port
        self.sub_port = sub_port

        self.domain = socket.AF_INET #IPV4
        if (device_connection[0:3] == "tcp"):
            self.data_type = socket.SOCK_STREAM #TCP
        else:
            self.data_type = socket.SOCK_DGRAM #UDP

        #Here is where I need help
        self.pub_sock = socket.socket(self.domain, self.data_type)
        self.pub_sock.bind((self.device_connection[6::], self.pub_port))

        self.sub_sock = socket.socket(self.domain, self.data_type)
        self.sub_sock.connect((self.device_connection[6::], self.pub_port))

import socket
import time
import threading

class Node:
    def __init__(self, node_name, device_connection = 'udp://127.0.0.101', node_connection_port = 5558):
        self._node_name = node_name
        self._device_connection = device_connection #connection, UDP or TCP
        self._node_connection_port = node_connection_port #Port to connect to
        self._binding_domain = socket.AF_INET #IPV4
        if(device_connection[0:3] == "tcp"):
            self._data_type = socket.SOCK_STREAM #If it's TCP, socket uses SOCKSTREAM
        elif(device_connection[0:3] == "udp"):
            self._data_type = socket.SOCK_DGRAM #DGRAM FOR UDP. ASSUMING ONE OR THE OTHER. HAVENT HANDLED INCORRECT INPUT YET
            
        #Dictionaries of pubs and subs
        self._node_pubs = {}
        self._node_subs = {}

    def create_publisher(self, topic, pub_port=5559):
        #Use publisher class to create a publisher
        new_pub = Node._Publisher(topic, self._device_connection, pub_port)
        self._node_pubs[pub_port] = new_pub
        return new_pub

    def create_subscriber(self, topic, sub_port=5559):
        #Use subscriber class to create a subscriber
        new_sub = Node._Subscriber(topic, self._device_connection, sub_port)
        self._node_subs[sub_port] = new_sub
        return new_sub

    class _Publisher:
        def __init__(self, topic, device_connection='udp://127.0.0.101', pub_port=5559):
         #Doesn't do anything
            self._topic = topic #Topics, like remote control, camera, AHRS, DVL, BACKPLANE,etc
            self._host = device_connection[6::] #udp and tcp both 3 letters, thank god
            self._domain = socket.AF_INET #IPV4
            if(device_connection[0:3] == "tcp"):
                self._data_type = socket.SOCK_STREAM #SOCKSTREAM FOR TCP
            elif(device_connection[0:3] == "udp"):
                self._data_type = socket.SOCK_DGRAM #DGRAM FOR UDP
            self._port = pub_port
            self._sock = socket.socket(self._domain, self._data_type) #CREATE A SOCKET

        def publish(self, message):
            self._sock.sendto(message.encode(), (self._host, self._port)) #HAVE THAT SOCKET PUBLISH MESSAGES
            return

    class _Subscriber:
        def __init__(self, topic, device_connection='udp://127.0.0.101', sub_port =5559):
            self._topic = topic #just see above tbh. same as publisher
            self._host = device_connection[6::]
            self._domain =  socket.AF_INET
            if(device_connection[0:3] == "tcp"):
                self._data_type = socket.SOCK_STREAM
            elif(device_connection[0:3] == "udp"):
                self._data_type = socket.SOCK_DGRAM
            self._port = sub_port
            self._sock = socket.socket(self._domain, self._data_type)
            self._sock.bind((self._host, self._port)) #This part is different. Bind to specified host

        def subscribe(self):
            message_data, message_addr = self._sock.recvfrom(1024) #send this many bytes of data at a time
            print(message_data)

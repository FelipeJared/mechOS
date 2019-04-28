import socket
import time
import mechos_base
import threading

class Node:
    def __init__(self, node_name, device_connection = 'tcp://127.0.0.101', node_connection_port = "5558"):
        self._node_name = node_name
        self._device_connection = device_connection
        self._node_connection_port = node_connection_port
        self._binding_domain = socket.AF_INET
        if(device_connection[0:3] == "tcp"):
            self._data_type = socket.SOCK_STREAM
        else:
            self._data_type = socket.SOCK_DGRAM

        self._pub_context = None
        self._sub_context = None
        self._callback_queue = None

        self._node_pubs = []
        self._node_subs = []

    def _connect_node_to_mechoscore(self):
        pass

    def create_publisher(self, topic, pub_port="5559"):
        new_pub = Node._Publisher(topic, self._pub_context, self._device_connection, pub_port)
        self._node_pubs.append(new_pub)
        return new_pub

    def create_subscriber(self, topic, callback, timeout=0.1, sub_port="5560"):
        new_sub = Node._Subscriber(topic, callback, self._sub_context, timeout, self._device_connection, sub_port)
        self._node_subs.append(new_sub)
        return new_sub

    def spinOnce(self, specific_subscriber=None, timeout=0.001):
        pass

    def print_something(self):
        print("Please work")

    class _Publisher:
        def __init__(self, topic, pub_context, device_connection='tcp://127.0.0.101', pub_port="5559"):
            pub_context = None
            self._topic = topic
            self._host = device_connection[6::] #udp and tcp both 3 letters, thank god
            self._domain = socket.AF_INET
            if(device_connection[0:3] == "tcp"):
                self._data_type = socket.SOCK_STREAM
            else:
                self._data_type = socket.SOCK_DGRAM
            self._port = pub_port
            self._sock = socket.socket(self._domain, self._data_type)

        def publish(self, message):
            self._sock.sendto(message.encode(), (self._host, self._port))
            return

    class _Subscriber:
        def __init__(self, topic, callback, context, timeout = 1, device_connection ='tcp://127.0.0.101', sub_port ="5560"):
            self._topic = topic
            self._host = device_connection[6::]
            self._domain =  socket.AF_INET
            if(device_connection[0:3] == "tcp"):
                self._data_type = socket.SOCK_STREAM
            else:
                self._data_type = socket.SOCK_DGRAM
            self._port = sub_port
            self._sock = socket.socket(self._domain, self._data_type)
            self._sock.bind((self._host, self._port))

        def _spinOnce(self):
            message_data, message_addr = self._sock.recvfrom(1024) #send this many bytes of data at a time
            print(message_data)

if __name__ == '__main__':
     node = Node("Shafi")
     callback = None
     context = None
     node.create_publisher("Shafi's stuff", 1345)
     node.create_subscriber("Shafi's stuff", callback, 1, 1346)

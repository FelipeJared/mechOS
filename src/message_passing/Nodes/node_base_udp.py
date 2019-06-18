"""Code for implementing the nodes using nodebase. Nodebase is an abstract class
that may send data either locally via RAM or over a network using UDP or TCP
connection. Will be used for any communication with the sub,including image
transfer, displaying data with the GUI, or accepting inputs from Xbox controller.

 ..moduleauthors:: Christian Gould <christian.d.gould@gmail.com>
                   Mohammad Shafi <ma.shafi99@gmail.com>
"""

import os
import sys
comm_path = os.path.join("..", "..")
sys.path.append(comm_path)

import time
import threading
import socket

from message_passing.communicationUtils import local as local
from message_passing.communicationUtils import network as network
from abc import ABC, abstractmethod


class node_base(ABC, threading.Thread):
    """This abstract classs inherits from threading.Thread, allowing it to
    receive all of its functions, like start, run, etc. Nodes are the means that
    we use to gather, store, send, and receive data, whether locally or via the
    network
    """
    def __init__(self, volatile_memory, ip_route):
        """A class we use to instantiate our nodes, and prepare them for local
        or network data transfer

        :param volatile_memory: The dictionary to store data for local transfer
        :type volatile_memory: dictionary
        :param ip_route: A dictionary that holds everything necessary for the
                         network transfer, like sockets, ip addresses, etc.
        :type ip_route: dictionary
        """
        threading.Thread.__init__(self)
        ABC.__init__(self)
        print(__class__.__name__,'inherited')

        self._publisher=network.publisher(ip_route)
        self._subscriber=network.subscriber(ip_route)

        self._reader=local.reader(volatile_memory)
        self._writer=local.writer(volatile_memory)

    def _send(self,  msg, register, local=True, foreign=False):
        """Sends your message to the address(s) provided, either foreign local
        or both
        :param msg: the message we want to send
        :type msg: bytes
        :param register: the key to access the local or network dictionary
        :type register: object
        :param local: specifies whether we send data locally or not
        :type local: bool
        :param foreign: specifies whether we send the data over the network
        :type foreign: bool
        :raises: KeyError, socket.gaierror, AttributeError
        """

        if foreign:
            self._publisher.publish(msg, register)
            if not local:
                return 0
        return self._writer.write(msg, register)    #I know this is a return
                                                    #statement, but it doesn't
                                                    #do shit. I'm still too
                                                    #scared to delete the return

    def _recv(self, register, local=True):
        """Receives message from the addresses provided, either local or
        :param register: the key for either the local or foreign dictionary we
                         attempt to subscribe to
        :type register: object
        :param local: specifies whether we are subscribing to data locally or
                      via the network
        :type local: bool
        :returns: object. Whatever is stored at the dictionary, bytes if socket
        :raises: KeyError, socket.gaierror, AttributeError
        """
        if not local:
            return self._subscriber.subscribe(register)
        else:
            return self._reader.read(register)

    @abstractmethod
    def run(self):
        """This method is abstract. Allows the node to perform any function we wish
        whether that is publishes, subscriptions, or even dumb print statements
        """
        pass

if __name__=='__main__':
    import time
    class WriteNode(node_base):
        """Example utilization of the writer
        """
        def __init__(self, IP, MEM):
            """Initializes the writing node
            :param IP: dictionary that holds information we need for network
            :type IP: dictionary
            :param MEM: dictionary that holds information for local transfer
            :type MEM: dictionary
            """
            node_base.__init__(self, MEM, IP)
            self._memory = MEM
            self._ip_route = IP
            self.MSG='uninitialized'
            self.baud=.128

        def set_message(self, message):
            """Standard setter method
            :param message: message we want to send locally
            :type message: object
            """
            self.MSG=message
        def set_baudrate(self, baudrate):
            """Also a standard setter method
            :param baudrate: set the rate for message sending
            :type baudrate: float
            :raises: AttributeError
            """
            self.baud=baudrate

        def run(self):
            """Until the user quits, continuously write to the specified
            location
            """
            start_time = time.time()
            while True:
                if ( (time.time() - start_time) >= self.baud ):
                    self._send(msg=self.MSG, register='Encrypted_dat')
                    start_time=time.time()
                else:
                    time.sleep(0)

    class PublishNode(node_base):
        """Example utilization of the publisher
        """
        def __init__(self, IP, MEM):
            """Initializes the publishing node
            :param IP: dictionary that holds information we need for network
            :type IP: dictionary
            :param MEM: dictionary that holds information for local transfer
            :type MEM: dictionary
            """
            node_base.__init__(self, MEM, IP)
            self._memory = MEM
            self._ip_route = IP
            '''
            PublisherNode:
            '''
            self.MSG = b'uninitialized'
            self.baud=.128

        def set_message(self, message):
            """
            :param message: message we want to send over the network
            :type message: bytes
            """
            self.MSG = message
        def set_baudrate(self, baudrate):
            """Also a standard setter method
            :param baudrate: set the rate for message sending
            :type baudrate: float
            :raises: AttributeError
            """
            self.baud = baudrate

        def run(self):
            """Until the user quits, continously publish the specified message
            via socket using UDP
            :raises: socket.gaierror
            """
            start_time = time.time()
            while True:
                if((time.time() - start_time) >= self.baud):
                    self._send(msg=self.MSG, register='Encrypted_dat', local=False, foreign=True)
                    start_time = time.time()
                else:
                    time.sleep(0)

    class ReadNode(node_base):
        """Example utilization of the reader
        """
        def __init__(self, IP, MEM):
            """Initializes the reading node
            :param IP: dictionary that holds information we need for network
            :type IP: dictionary
            :param MEM: dictionary that holds information for local transfer
            :type MEM: dictionary
            """
            node_base.__init__(self, MEM, IP)
            self._memory = MEM
            self._ip_route = IP
            self.baud=.128

        def run(self):
            """Continuouly reads from local memory until the user quits
            """
            start_time = time.time()
            while True:
                if ( (time.time() - start_time) >= self.baud ):
                    print(self._recv('Encrypted_dat')) # Local True By Default
                    start_time=time.time()
                else:
                    time.sleep(0)

    class SubscribeNode(node_base):
        """Example utilization of the subscriber node
        """
        def __init__(self, IP, MEM):
            """Initializes the publishing node
            :param IP: dictionary that holds information we need for network
            :type IP: dictionary
            :param MEM: dictionary that holds information for local transfer
            :type MEM: dictionary
            """
            node_base.__init__(self, MEM, IP)
            self._memory = MEM
            self._ip_route = IP
            self.baud=.105

            '''
            self.address = list(IP)[0]
            print(self._ip_route)
            '''

        def run(self):
            """Continously subscribes from the specified socket via UDP until
            the user quits
            :raises:socket.gaierror
            """
            start_time = time.time()
            while True:
                if ((time.time() - start_time) >= self.baud):
                    print(self._recv('Encrypted_dat', local=False))
                    start_time = time.time()
                else:
                    time.sleep(0)

    # Volatile Memory Instances
    pub_socket1=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sub_socket1=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    pub_socket2=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sub_socket2=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Dictionary

    ip_address1 = ('127.0.0.101', 5558)
    ip_address2 = ('127.0.0.101', 5559)

    sub_socket1.bind((ip_address1))
    sub_socket2.bind((ip_address2))
    #Dictionary with key: ip address, value is tuple with publisher/subscriber socket
    """This protocol below for the IP dictionaries that we use for publishers
    and subscribers MUST be maintained. Has to be set like this
    """
    IP={'Encrypted_dat':
                {
                 'address':ip_address1,
                 'sockets':(pub_socket1, sub_socket1),
                 'type':'UDP'
                },
	'Doesnt matter':
                {
                 'address':ip_address2,
                 'sockets':(pub_socket2, sub_socket2),
                 'type':'UDP'
                }
        }

    MEM={'Velocity_x':12.01,'Velocity_y':12.02,'Velocity_z':12.03,'Encrypted_dat':'None'}

    # Initialize Node
    MyWriteNode = WriteNode(IP, MEM)
    #print(MyWriteNode._ip_route)
    MyPublishNode = PublishNode(IP, MEM)
    MyReadNode  = ReadNode(IP, MEM)
    MySubscribeNode = SubscribeNode(IP, MEM)
    #print(MyReadNode._ip_route)

    # Start Thread
    MyWriteNode.start()
    MyPublishNode.start()
    MyReadNode.start()
    MySubscribeNode.start()

    MyWriteNode.set_message('OUTPUT A')

    MyPublishNode.set_message(b'OUTPUT B')

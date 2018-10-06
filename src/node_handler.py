import zmq
from zmq.devices.basedevice import ProcessDevice
import mechos
import sys
import time

class _Node_Handler:
    '''
    This class is for MechOSCore to be able to communicate with, control, and
    monitor individual nodes. Its primary function is to store realtime data
    about running nodes. It also makes sure nodes are unique and has the ability
    to takedown nodes.
    '''
    def __init__(self):
        '''
        Initialize the node handler. Starts up server to communicate with
        nodes.
        '''
        pass

    def listen_and_connect_available_node(self):
        '''
        Listen for nodes trying to connect to mechoscore and connect them.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        pass
    def _connect_node(self, ):
        '''
        Connect an already non-connected node to mechos if it is unique and
        does not already exist. Raise an error that node could not connect
        if it is not unique. If the node is allowed to connect, it will send
        confirmation to the node to begin communication.

        Parameters:
            N/A
        Returns:
            connected: True if connection successful, false otherwise
        '''
        pass
    def _kill_node(self, node_name):
        '''
        Kill a node connected to mechoscore by specifying the unique
        nodes name.

        Parameters:
            node_name: The unique name of a node connected to the network
        '''
        pass
class _Pub_Sub_Handler:
    '''
    Communication link for publisher/subscribers. Utilize zmq devices to
    to automatically rout publisher messages to subscribers of the same topic
    name.
    '''
    def __init__(self, device_connection="tcp://127.0.0.101", pub_port="5559",
                    sub_port="5560"):
        '''
        Set up the pub_sub_handler socket connections

        Parameters:
            device_connection: The tcp IP of the mechoscore to connect to.
                                Default is tcp://127.0.0.101
            pub_port:The tcp socket that publishers will connect to.
            sub_port: The tcp socket that subscribers will connect to.
        '''
        self._device_connection = device_connection
        self._pub_port = pub_port
        self._sub_port = sub_port

        self._pub_connection_socket = self._device_connection + ":" + pub_port
        self._sub_connection_socket = self._device_connection + ":" + sub_port

        #device running as an isolated process that routes pub/sub messages
        self._pub_sub_handler_device = ProcessDevice(zmq.FORWARDER, zmq.SUB,
                                                    zmq.PUB)
        self._pub_sub_handler_device.bind_in(self._pub_connection_socket)
        self._pub_sub_handler_device.bind_out(self._sub_connection_socket)

        self._pub_sub_handler_device.setsockopt_in(zmq.SUBSCRIBE,
                                                    "".encode("utf-8"))
    def start_pub_sub_handler(self):
        '''
        Start the isolated process that routes publisher messages to subscribers
        This process will be terminated once python script terminates
        Parameters:
            N/A
        Returns:
            N/A
        '''
        self._pub_sub_handler_devce.start()

if __name__ == "__main__":

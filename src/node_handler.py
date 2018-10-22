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
    def __init__(self, device_master_connection='tcp://127.0.0.101',
                    master_pub_port="5557", master_sub_port="5558"):
        '''
        Initialize the node handler. Starts up server to communicate with
        nodes.

        Parameters:
            device_master_connection: The tcp IP of the mechoscore to connect to.
                                Default is tcp://127.0.0.101
            master_pub_port: Port to publish messages to nodes using name as
                                the topic
            master_sub_port: Port the subscribe to receive message from nodes
        '''
        self._device_master_connection = device_master_connection
        self._master_pub_port = master_pub_port
        self._master_sub_port = master_sub_port
        self.connected_nodes = []

        #create a mechoscore node handler node
        self.master_node = mechos.Node("mechoscore", self._device_master_connection,
                                    _conn_mechoscore=False)

        #create a publisher for mechoscore to communicate to nodes
        self.master_node_publisher = self.master_node.create_publisher(
                                    "mechoscore", self._master_pub_port)

        #create a subscriber for mechoscore to receive messages from nodes
        self.master_node_subscriber = self.master_node.create_subscriber("node_connect",
                                        self._node_messages,
                                        sub_port=self._master_sub_port)

        #pub/sub handler for communication between nodes
        self.node_comm_handler = _Pub_Sub_Handler(self._device_master_connection,
                                self._master_pub_port, self._master_sub_port)
        self.node_comm_handler.start_pub_sub_handler()

    def _node_messages(self, node_data):
        '''
        Receive information directly from nodes to get their individual status.

        Paramters:
            node_data: Data being received by the mechoscore
        '''

        data = node_data.decode().split("/")
        #connect any nodes attempting to connect
        if(data[2] == "connect"):
            #connecting nodes have the form "[node_name]/connect"
            self.connected_nodes.append(data[1])
            self.master_node_publisher.publish(data[1] + "/connect")
            print("Node", data[1], "connecting to mechoscore.")

    def listen_and_connect_available_node(self):
        '''
        Listen for nodes trying to connect to mechoscore and connect them.

        Parameters:
            N/A

        Returns:
            N/A
        '''

    def _connect_available_node(self):
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

        #Check if any nodes are trying to connect/communicate
        self.master_node.spinOnce()
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
        print("Pub/Sub Handler routing routing publisher messages from",
                self._pub_connection_socket, "to subscribers connected to",
                self._sub_connection_socket)
        self._pub_sub_handler_device.start()

if __name__ == "__main__":
    device_connection = "tcp://127.0.0.101"
    node_handler = _Node_Handler(device_connection)
    pub_sub_handler = _Pub_Sub_Handler(device_connection)
    pub_sub_handler.start_pub_sub_handler()
    while(1):
        node_handler._connect_available_node()

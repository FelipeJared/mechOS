import zmq
from multiprocessing import Process
import time

class Node:
    '''
    Nodes are a objects with the ability to perform a variety of node graph
    based communication. Each node created connects to a common Master node. A
    node contains multiple communication gateways such as pub/sub, pull/req, and
    services.
    '''
    def __init__(self, node_name, device_connection='tcp://127.0.0.101',
                node_pub_port="5557", node_sub_port="5558", _conn_mechoscore = True):
        '''
        Initialize a node and connect to the master mechoscore.

        Parameters:
            node_name: The name of the node
            device_connection: The tcp IP of the mechoscore to connect to.
                                Default is tcp://127.0.0.101
            node_pub_port: The port used by the node to publish status
                                messages to mechoscore.
            node_sub_port: The port used by the node to subscribe to mechoscore
                            messages.
            _conn_mechoscore: If true, have the node connect to mechoscore.
                                Default True.
        Returns:
            N/A
        '''
        self._node_name = node_name
        self._device_connection = device_connection
        self._node_pub_port = None
        self._node_sub_port = None
        self._conn_mechoscore = _conn_mechoscore

        #Only a single publihser/subscriber context should be made per one node. Since
        #each node runs in a single process.
        self._pub_context = zmq.Context()
        self._sub_context = zmq.Context()

        #keep a list of publishers/susbscribers in node for information purposes
        self._node_pubs = []

        #dictionary mapping subscriber sockets to subscriber objects
        self._node_subs = {}

        #set to queue up all subscriber callback to be ran at each spinOnce
        self._callback_queue = set()

        #Set up a zmq poller to poll subscriber messages
        self._sub_poller = zmq.Poller()

        #Connect node to mechoscore
        if(self._conn_mechoscore):
            self._node_pub_port = node_pub_port
            self._node_sub_port = node_sub_port
            self._connect_node_to_mechoscore()

    def _mechos_messages(self, mechoscore_data):
        '''
        Receive messages from mechoscore and process messages based on content

        Parameters:
            mechoscore_data: The data giving an action to nodes from mechoscore
        '''
        data = mechoscore_data.decode().split("/")
        if((data[1] == self._node_name) and (data[2] == "connect")):
            self._node_connected = True

    #TODO: create pair (client/server) of node with mechoscore
    def _connect_node_to_mechoscore(self):
        '''
        Connect each node instance to mechoscore. First check that mechoscore is
        started by receiving a confirmation from mechoscore that it is running.
        Also check from mechoscore that there are not any other nodes of the
        same name. Each node will be a client to mechoscore which is the server

        Parameters:
            N/A
        Returns:
            N/A
        '''
        #Create node communication to mechoscore
        self.node_publisher_to_mechoscore = self.create_publisher("node_connect",
                                                self._node_pub_port)
        self.node_subscriber_to_mechoscore = self.create_subscriber("mechoscore",
                                    self._mechos_messages, sub_port=self._node_sub_port)

        #connect to mechoscore
        self._node_connected = False
        connection_message = ("%s/connect" % self._node_name)

        while not self._node_connected:
            #emit message specifying that the node is ready to connect
            self.node_publisher_to_mechoscore.publish(connection_message)
            #listen for message from mechoscore allowing the node to connect
            self.spinOnce()
        print("Node", self._node_name, "successfully connected to mechoscore.")
        return
    def create_publisher(self, topic, pub_port="5559"):
        '''
        Create a publisher from pub_context, and connect it to the mechoscore
        pub/sub handler to communicate using the topic name.

        Paramters:
            topic:A well-defined topic name to publish messages to
            pub_port: The port to connect the socket the publisher to
                        mechoscore. Default 5559
        Returns:
            N/A
        '''

        new_pub = Node._Publisher(topic, self._pub_context,
                                    self._device_connection, pub_port)

        #TODO: Have node store information about newly created publishers
        self._node_pubs.append(new_pub)

        return new_pub

    def create_subscriber(self, topic, callback, timeout=1, sub_port="5560"):
        '''
        Create a subscriber and connect it to mechoscore pub/sub handler to
        receiver data from a publisher using the same topic name.

        Parameters:
            topic: A well-defined topic name for subscriber to connect to
                    publisher of the same name.
            callback: A function to place the data received by the
                        subscriber. The first paramter of the callback
                        function is where the data will be passed.
            timeout: The time in seconds the poller will hold before
                    exiting if no messages are received. Keeps the direct
                    listening of messages from freezing up. Default 1 second
            sub_port: The port to connect the subscriber socket to mechoscore.
                        Default 5560
        Returns:
            N/A
        '''
        new_sub = Node._Subscriber(topic, callback, self._sub_context,
                                    timeout, self._device_connection, sub_port)

        #TODO: Have node store information about newly created subscribers
        self._callback_queue.add(callback)
        self._node_subs[new_sub._sub_socket] = new_sub

        #register new subscription to subscription _sub_poller
        self._sub_poller.register(new_sub._sub_socket, zmq.POLLIN)

        return new_sub

    def spinOnce(self, timeout=0.001):
        '''
        Attempt to retrieve a message from each subscriber and pass message to
        respective callback. Currently this is a single thread.

        Parameters:
            timeout: Time to wait for polling messages before continuing. T
        Returns:
            N/A
        '''

        socket_messages = dict(self._sub_poller.poll(timeout))

        for _sub_socket in socket_messages:
            if(_sub_socket in self._node_subs
                and socket_messages[_sub_socket] == zmq.POLLIN):

                #get single message from a single subscriber if message available
                self._node_subs[_sub_socket]._spinOnce()

        return

    class _Publisher:
        '''
        Publisher is a interprocess communication data emitter that publishes
        data of a specified type to a well-defined topic name. The mechoscore
        will route individual publisher data via the topic name to subscribers
        of the same topic.
        '''

        def __init__(self, topic, pub_context,
                    device_connection='tcp://127.0.0.101', pub_port="5559"):
            '''
            Initialize a publisher by connecting to the pub/sub handler running
            in the mechoscore.By default, publishers connect to
            tcp://localhost:5559.

            Parameters:
                topic: A well-defined topic name to publish messages to
                pub_context: The zmq context to keep control of all the
                            publishers in the node.
                device_connection: The TCP IP address to connect to. Default is
                                    tcp://127.0.0.101
                pub_port: The tcp socket to connect the publisher socket to.
            '''
            self._topic = topic
            self._pub_port = pub_port
            self._socket_connection = device_connection + (":%s" % self._pub_port)
            print(self._pub_port)
            #create a publisher socket connection
            self._pub_socket = pub_context.socket(zmq.PUB)

            print("Waiting to connect publisher", topic,
                    "to socket", self._socket_connection, "...")
            self._pub_socket.connect(self._socket_connection)

            print("Publisher", self._topic, "successfully connected")

        def publish(self, message):
            '''
            Publish message to topic. Message + topic are sent to mechoscore
            to be routed to subscribers.

            Parameters:
                message: A string of ASCII bytes

            Returns:
                N/A
            '''
            encoded_message = (("%s/%s" % (self._topic, message)).encode("utf-8"))
            self._pub_socket.send(encoded_message)
            return

    class _Subscriber:
        '''
        Subscriber is an interprocess communication receiver for the
        pub/sub protocol. Each subscriber subscribes to a topic through
        a well-defined name, and will listen to messages being routed
        from mechoscore from publishers.
        '''
        def __init__(self, topic, callback, context, timeout=1,
                        device_connection='tcp://127.0.0.101', sub_port="5560"):
            '''
            Initialize the parameters for a subscriber

            Parameters:
                topic:  A well-defined topic name for subscriber to listen to
                callback: A function to place the data received by the
                            subscriber. The first paramter of the callback
                            function is where the data will be passed.
                context: The zmq context for creating sockets
                timeout: The time in seconds the poller will hold before
                        exiting if no messages are received. Keeps the direct
                        listening of messages from freezing up.
                device_connection: device_connection: The tcp IP of the mechoscore to connect to.
                                    Default is tcp://127.0.0.101
                sub_port: The port to connect the subscriber topic to.
            '''
            self._sub_port = sub_port
            self._topic = topic
            self._callback = callback
            self._timeout = timeout
            self._sub_context = context

            self._sub_socket = self._sub_context.socket(zmq.SUB)
            self._socket_connection = device_connection + (":%s" % self._sub_port)

            #connect subscriber socket to mechoscore
            print("Waiting to connect subscriber", self._topic, "to",
                    self._socket_connection, "...")
            self._sub_socket.connect(self._socket_connection)
            self._sub_socket.setsockopt(zmq.SUBSCRIBE, self._topic.encode("utf-8"))
            print("Subscriber", self._topic, "successfully connected.")

        def _spinOnce(self):
            '''
            Receive a single message into subscriber and pass message to the
            subscribers given callback.

            Parameters:
                N/A
            Returns:
                N/A
            '''
            message_data = self._sub_socket.recv(zmq.NOBLOCK)
            self._callback(message_data)

import socket
import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client
import uuid
import os
import atexit
import time
import signal
import io
import math
import sys


class Node:
    '''
    A Node contains network communication members such as publishers and subscribers
    that communicate to other publishers and subscribers of other nodes. Nodes will
    register themselves (and their publishers and subscribers) with mechsocore. The node
    communicates with the master (mechoscore) via xmlrpc servers.
    '''
    def __init__(self, name, node_ip='127.0.0.1', mechoscore_ip='127.0.0.1', mechoscore_port=5959):
        '''
        Initialize a node by connecting it to the mechos network.

        Parameters:
            name: A unique name that any nodes in the network do no already have.
            node_ip: Default '127.0.0.1': The ip of the node (and the xmlrpc server running on the node)
            mechoscore_ip: Default '127.0.0.1'. The ip of mechsocore server.
            mechoscore_port: Default 5959: The port of the mechoscore server.
        '''
        self.name = name
        self.pid = os.getpid()
        self.ip = node_ip

        self.xmlrpc_server_ip = node_ip
        self.xmlrpc_server_port = self.get_free_port(node_ip)

        self.mechoscore_xmlrpc_server_ip = mechoscore_ip
        self.mechoscore_xmlrpc_server_port = mechoscore_port

        #Create an xml rpc server of the node so the master can make requests
        #to the node
        self._create_xmlrpc_server()

        #Create an xmlrpc client so the node can make request to mechoscore master.
        self._create_xmlrpc_client()

        #At exit of a program running a node, call to unregister function
        atexit.register(self.xmlrpc_client.unregister_node, self.name)

        #Dictionary that hold publisher create through this node
        self.node_publishers = {}

        #Dictionary that holds subscribers created through this node
        self.node_subscribers = {}

        #Register the node with mechoscore
        allowable = self.xmlrpc_client.register_node(self.name, self.pid,
                                    self.xmlrpc_server_ip, self.xmlrpc_server_port)
        if(not allowable):
            print("[ERROR]:Node %s already exists, killing program" % self.name)
            self.xmlrpc_client.unregister_node(self.name)

    def get_free_port(self, ip):
        '''
        Get a free port to connect to.

        Parameters:
            ip: The ip address to find a free port on.
        Returns:
            port: The free port number to be used.
        '''
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((ip,0))
            port = s.getsockname()[1]
        return(port)

    def _create_xmlrpc_server(self):
        '''
        Create the xmlrpc server for the node to establish communication
        with the rest of the network.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        #Create a simple xmlrpc server
        self.xmlrpc_server = SimpleXMLRPCServer((self.xmlrpc_server_ip, self.xmlrpc_server_port), logRequests=False)

        #Register functions with server
        #Update a publisher on a subscriber trying to connect. Allow it to make a
        #connection.
        self.xmlrpc_server.register_function(self._update_publisher)
        self.xmlrpc_server.register_function(self._update_subscriber)
        self.xmlrpc_server.register_function(self._kill_node)

        self.xmlrpc_server.register_function(self._kill_publisher)
        self.xmlrpc_server.register_function(self._kill_subscriber)

        self.xmlrpc_server.register_function(self._kill_subscriber_connection)
        self.xmlrpc_server.register_function(self._kill_publisher_connection)

        #Run the nodes xmlrpc server as a thread.
        self.xmlrpc_server_thread = threading.Thread(target=self.xmlrpc_server.serve_forever, daemon=True)
        self.xmlrpc_server_thread.start()

    def _create_xmlrpc_client(self):
        '''
        Create an xmlrpc server client to establish communication from this node
        to mechsocore.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        self.xmlrpc_client = xmlrpc.client.ServerProxy("http://" + \
                    self.mechoscore_xmlrpc_server_ip + ":" + \
                    str(self.mechoscore_xmlrpc_server_port))

    def _kill_node(self):
        '''
        Kill the process (pid) that this node is running on.

        Parameters:
            None
        Returns:
            True
        '''

        os.kill(self.pid, signal.SIGTERM)
        return(True)

    def _update_publisher(self, publisher_id, subscriber_id, subscriber_ip, subscriber_port):
        '''
        XMLRPC CALL FROM MECHOSCORE

        Update the publisher on what subscribers to connect to. Use the subscribers id
        ip, and port to allow either tcp or udp connection.

        Parameters:
            publisher_id: A unique id that was generated on the creation
                        of the publisher.
            subscriber_id: A unique id of the subscriber to connect to the publisher having
                        publisher id.
        '''
        publisher = self.node_publishers[publisher_id]

        if(publisher.protocol == "tcp"):

            publisher_accept_thread = threading.Thread(target=self._publisher_accept_connection, args=[publisher_id, subscriber_id], daemon=True)
            publisher_accept_thread.start()
            #allow the publish to accept tcp connection.
            #self._publisher_accept_connection(publisher_id, subscriber_id)

        #Udp publishers don't need to accept a connection to send
        elif(publisher.protocol == "udp"):

            #Note that update subscribers was called first
            publisher.subscriber_udp_connections[subscriber_id] = [subscriber_ip, subscriber_port]
        return True

    def _publisher_accept_connection(self, publisher_id, subscriber_id):
        '''
        When a subscriber is requesting to establish tcp connection with a publisher
        having publisher_id, allow the subscriber to connect.

        Parameters:
            publisher_id: The unique id of the publisher that needs to allow the
                            subscriber with subscriber id to connect.
            subscriber_id: The unique id of the subscriber trying to connect to the publisher.
                            It may be from this node or a different node.
        '''

        publisher = self.node_publishers[publisher_id]

        conn, addr = publisher.server_socket.accept()
        conn.setblocking(False)

        #Maximum send buffer.
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, publisher.queue_size*publisher.message_format.size)
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        publisher.subscriber_tcp_connections[subscriber_id] = [conn, addr]


    def _update_subscriber(self, subscriber_id, publisher_id, publisher_ip, publisher_port):
        '''
        XMLRPC CALL FROM MECHOSCORE

        Request from mechoscore for the subscriber with the given id to add a new connection
        to the provided publisher.

        Parameters:
            subscriber_id: The unique id of the subscribe to update.
            publisher_id: The unique id of the publisher that the subscriber is trying to connect to.
            publisher_ip: The ip address of the publisher that the subscriber should connect to.
            publisher_port: The port number of the publisher that the subscriber should connect to.
        Returns:
            True
        '''

        subscriber = self.node_subscribers[subscriber_id]

        if(subscriber.protocol == "tcp"):
            subscriber._connect_to_tcp_publisher(publisher_id, publisher_ip, publisher_port)

        elif(subscriber.protocol == "udp"):
            subscriber._connect_to_udp_publisher(publisher_id, publisher_ip, publisher_port)

        return True

    def _kill_publisher(self, id):
        '''
        XMLRPC CALL FROM MECHOSCORE

        Unregister a publisher from the node and kill the publisher.

        Parameters:
            id: The unique id to access the publisher to be able to kill it.
        Returns:
            True
        '''
        publisher = self.node_publishers[id]

        subscriber_ids = list(publisher.subscriber_tcp_connections.keys()).copy()

        if(publisher.protocol == "tcp"):
            #Close all the connection to the subscribers.
            for subscriber_id in subscriber_ids:

                #close the connection socket to the subscriber on the publishers end.
                (publisher.subscriber_tcp_connections[subscriber_id])[0].close()

                #Remove the socket connecting to the subscriber
                (publisher.subscriber_tcp_connections.pop(subscriber_id))

        #close the udp server socket.
        elif(publisher.protocol == "udp"):
            subscriber_ids = list(publisher.subscriber_udp_connections.keys()).copy()

            for subscriber_id in subscriber_ids:

                #remove all the subscribers connected to this udp
                publisher.subscriber_udp_connections.pop(subscriber_id)

            publisher.server_socket.close()


        #Remove the publisher from the nodes publisher dictionary
        self.node_publishers.pop(id)
        del publisher

        return True

    def _kill_subscriber(self, id):
        '''
        XMLRPC CALL FROM MECHOSCORE

        Unregister a subscriber from the node and kill the subscriber.

        Parameters:
            id: The unique id to access the subscriber
        Returns:
            True
        '''
        subscriber = self.node_subscribers[id]

        #Close all the connections to publishers.
        for publisher_id in self.node_publishers.keys():
            publisher = self.node_publishers[publisher_id]

            if(publisher.protocol == "tcp"):
                #close the subscriber client connection
                (subscriber.publisher_tcp_connections[publisher_id]).close()
                subscriber.publisher_tcp_connections.pop(publisher_id)

            elif(publisher.protocol == "udp"):
                (subscriber.publisher_udp_connections[publisher_id])[0].close()
                subscriber.publisher_udp_connections.pop(publisher_id)

        self.node_subscribers.pop(id)
        del subscriber

        return(True)

    def _kill_subscriber_connection(self, publisher_id):
        '''
        XMLRPC CALL FROM MECHOSCORE

        Kill all subscriber connections to a publisher with publisher id.

        Parameters:
            publisher_id: The id of the publisher that the subscriber should disconnect
                        from.
        Returns:
            True
        '''

        for subscriber_id in self.node_subscribers.keys():

            subscriber = self.node_subscribers[subscriber_id]

            #if subscriber is tcp
            if(publisher_id in subscriber.publisher_tcp_connections.keys()):
                (subscriber.publisher_tcp_connections[publisher_id]).close()
                subscriber.publisher_tcp_connections.pop(publisher_id)

            #if subscriber is udp
            elif(publisher_id in subscriber.publisher_udp_connections.keys()):
                (subscriber.publisher_udp_connections[publisher_id])[0].close()
                subscriber.publisher_udp_connections.pop(publisher_id)


        return True

    def _kill_publisher_connection(self, subscriber_id):
        '''
        '''
        for publisher_id in self.node_publishers.keys():

            publisher = self.node_publishers[publisher_id]

            #if publisher is tcp
            if(subscriber_id in publisher.subscriber_tcp_connections.keys()):

                publisher.subscriber_tcp_connections[subscriber_id][0].close()
                publisher.subscriber_tcp_connections.pop(subscriber_id)

        return True

    def create_publisher(self, topic, message_format, queue_size=1000, ip=None, protocol="tcp"):
        '''
        Create either a tcp or udp publisher server.

        Parameters:
            topic: A well-defined topic name for subscriber to connect to the publisher
                    of the same name
            message_format: A message type format object that contains a pack and unpack
                            method for packing and unpacking bytes. It also must have the
                            byte size of the message.
            ip: The ip address that you want to connect publishers server to be created on.
            port: The port address that you want to connect the publishers server to.
            protocol: Either tcp or udp protocol. Note only one topic can have one protocol.
        '''
        if ip == None:

            ip=self.ip

        port = self.get_free_port(ip)
        #port = 8787
        publisher = Node.Publisher(topic, message_format, queue_size, ip, port, protocol)

        #Add the publisher object to the node dictionary of publishers.
        self.node_publishers[publisher.id] = publisher

        if(protocol == "tcp"):
            publisher._create_tcp_server()
        elif(protocol == "udp"):
            publisher._create_udp_server()

        allowable = self.xmlrpc_client.register_publisher(self.name, publisher.id, publisher.topic,
                                publisher.ip, publisher.port, publisher.protocol)



        return publisher

    def create_subscriber(self, topic, message_format, callback, queue_size=1000, ip=None, protocol="tcp"):
        '''
        Create either a tcp or udp subscriber that will connect to publishers
        when instructed to by mechoscore.

        Parameters:
            topic: A well-defined topic name that some publisher will emit data from.
            callback: A function with one parameter in which the subscriber will pass the
                        data it receives to.
            protocol: Either tcp or udp protocol
        '''
        if ip == None:

            ip=self.ip

        port = self.get_free_port(ip)
        subscriber = Node.Subscriber(topic, message_format, callback, queue_size, ip, port, protocol)

        #Add the subscriber to the node subscriber list.
        self.node_subscribers[subscriber.id] = subscriber

        allowable = self.xmlrpc_client.register_subscriber(self.name, subscriber.id,
                                        subscriber.topic, subscriber.ip, subscriber.port, subscriber.protocol)

        return(subscriber)
    def spin_once(self):
        '''
        Check for messages for each subscriber of the node.

        Parameters:
            N/A
        Returns:
            N/A
        '''

        for subscriber_id in self.node_subscribers.keys():

            #Receive message
            subscriber = self.node_subscribers[subscriber_id]
            message = subscriber._receive()

    class Publisher:
        '''
        Publisher is a tcp/udp data emitter that publishes data of a specific
        type to a well-defined topic name. The publisher will be registered with
        mechoscore through the mechoscore XMLRPC server and will be connected to subscriber
        throught the Node XMLRPC server.
        '''
        def __init__(self, topic, message_format, queue_size, ip, port, protocol):
            '''
            Create either a tcp or udp publisher server.

            Parameters:
                topic: A well-defined topic name for subscriber to connect to the publisher
                        of the same name
                ip: The ip address that you want to connect publishers server to be created on.
                port: The port address that you want to connect the publishers server to.
                protocol: Either tcp or udp protocol. Note only one topic can have one protocol.
            '''
            self.topic = topic
            self.queue_size = queue_size
            self.ip = ip
            self.port = port
            self.protocol = protocol

            self.message_format = message_format

            #generate a unique id
            self.id = str(uuid.uuid4().hex)

            #The socket connections of subscribers when the accpet() function is called.
            self.subscriber_tcp_connections = {}

            #Hold the ip and port of the subscribers to send to over udp
            self.subscriber_udp_connections = {}

        def _create_tcp_server(self):
            '''
            If the publisher is has a tcp protocol, then create a tcp socket server.

            Parameters:
                N/A
            Returns:
                N/A
            '''


            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.queue_size*self.message_format.size)
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen()

        def _create_udp_server(self):
            '''
            If the publisher is has a udp protocol, then create a udp socket server.

            Parameters:
                N/A
            Returns:
                N/A
            '''

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.queue_size*self.message_format.size)


        def publish(self, message):
            '''
            Publish a message to the topic of the subscriber. Note the message must
            be of 'utf-8' type.

            Parameters:
                message: A 'utf-8' type message to publish

            Returns
                N/A
            '''

            message_encoded = self.message_format._pack(message)
            if(self.protocol == 'tcp'):

                subscriber_connections = list(self.subscriber_tcp_connections.keys()).copy()
                for subscriber_id in subscriber_connections:
                    try:
                        sub_socket = (self.subscriber_tcp_connections[subscriber_id])[0]
                        sub_socket.send(message_encoded)
                    except socket.error as e:
                        print("[ERROR]: A socket has appeared to disconnect")
                        continue
                    except:
                        continue
            elif(self.protocol == 'udp'):
                
                subscriber_connections = list(self.subscriber_udp_connections.keys()).copy()
                for subscriber_id in subscriber_connections:
                    try:
                        [subscriber_ip, subscriber_port] = self.subscriber_udp_connections[subscriber_id]

                        self.server_socket.sendto(message_encoded, (subscriber_ip, subscriber_port))

                    except socket.error as e:
                        continue
                    except:
                        continue

    class Subscriber(threading.Thread):
        '''
        Subscriber is a tcp/udp data receiver that receives data from publishers based on a
        a topic name. The subscriber will be registered with mechoscore through the mechoscore XMLRPC server and will be connected to subscriber
        throught the Node XMLRPC server.
        '''
        def __init__(self, topic, message_format, callback, queue_size, ip, port, protocol):
            '''
            Create either a tcp or udp subscriber to the following topci

            Parameters:
                topic: The name of the topic to subscribe to for data.
                protocol: the protocol that the publishers of the given topic will
                        publish on.

                callback: A function with one parameter in which the subscriber will pass the
                            data it receives to.
            '''

            #Initialize base thread class
            threading.Thread.__init__(self)

            self.topic = topic
            self.protocol = protocol
            self.callback = callback
            self.queue_size = queue_size

            self.message_format = message_format

            #generate a unique id
            self.id = str(uuid.uuid4().hex)

            self.daemon = True
            self.run_thread = True

            self.ip = ip
            self.port = port

            #A dictionary where the key is the unique id of the publisher and
            #the value is the socket connection object.
            self.publisher_tcp_connections = {}
            self.publisher_udp_connections = {}

        def _connect_to_tcp_publisher(self, publisher_id, publisher_ip, publisher_port):
            '''
            Connect to a tcp publisher when notified by mechoscore that there is a publisher that
            the subscriber is unconnected to.

            Parameters:
                publisher_id: The publisher id to to establish connection with.
                ip: The ip of the publisher.
                port: The port of the publisher
            '''
            sub_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sub_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sub_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.queue_size*self.message_format.size)
            sub_socket.bind((self.ip, self.port))
            sub_socket.connect((publisher_ip, publisher_port))

            #Set socket to non-blocking
            sub_socket.setblocking(False)

            self.publisher_tcp_connections[publisher_id] = sub_socket


        def _connect_to_udp_publisher(self, publisher_id, publisher_ip, publisher_port):
            '''
            '''
            sub_socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_DGRAM)
            sub_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.queue_size*self.message_format.size)
            sub_socket.bind((self.ip, self.port))
            sub_socket.setblocking(False)
            self.publisher_udp_connections[publisher_id] = [sub_socket, publisher_ip, publisher_port]


        def _receive(self):
            '''
            For each socket connected to a publisher, try to receive any data
            if possible.

            Parameters:
                buffer_size: The maximum number of bytes to read for each message
            Returns:
                N/A
            '''
            if(self.protocol == "tcp"):

                for publisher_id in self.publisher_tcp_connections.keys():
                    try:


                        message_encoded = self.publisher_tcp_connections[publisher_id].recv(self.message_format.size)

                        if(not message_encoded):
                            continue

                        message = self.message_format._unpack(message_encoded)
                        self.callback(message)


                    except socket.error as e:
                        continue

            elif(self.protocol == "udp"):


                for publisher_id in self.publisher_udp_connections.keys():

                    try:

                        message_encoded, _ = self.publisher_udp_connections[publisher_id][0].recvfrom(self.message_format.size)

                        if(not message_encoded):
                            continue

                        message = self.message_format._unpack(message_encoded)
                        self.callback(message)

                    except socket.error as e:
                        continue
                    except:
                        continue

class Parameter_Server_Client():
    '''
    This creates an object that is a client to the parameter server running on
    mechoscore.
    '''
    def __init__(self, ip=None, port=None):
        '''
        Initialize Parameter server for XMLRPCServer client.
        Parameters:
            ip: The ip address to host the XMLRPCServer. Default "http://127.0.0.101"
            port: The port to host the XMLRPCServer. Default 8000
        Returns:
            N/A
        '''
        if ip == None:
            ip = "127.0.0.1"

        if port == None:
            port = 8000

        self.client = xmlrpc.client.ServerProxy("http://" + ip + ":" + str(port))
    def use_parameter_database(self, xml_file):
        '''
        Sets the xml file to use for the parameter server to store and retreive
        data from.
        Parameters:
            xml_file: The xml file to save and get parameters from.
        Returns:
            true
        '''
        self.client.use_parameter_database(xml_file)

    def set_param(self, param_path, parameter):
        '''
        Set a parameter in the the xml file database. If the parameter path already
        exist, then update its content with the new parameters. If the parameter
        path does not exist, create the parameter path and add the parameter value.
        Parameter:
            param_path: The parameter path tree to set the given parameter. Note:
                        each level name should be spaced by a '/'.
                        Example 'PID/roll_pid/p'
            parameter: The string representation of the parameter you want to set.
        Returns:
            N/A
        '''
        self.client.set_param(param_path, parameter)
        return True

    def get_param(self, param_path):
        '''
        Get the parameter from the given parameter_path. If the parameter does not
        exist, through an error.
        Parameters:
            param_path: The parameter path tree to set the given parameter.
        Returns:
            N/A
        '''
        parameter = self.client.get_param(param_path)
        return parameter

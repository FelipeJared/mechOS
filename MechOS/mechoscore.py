import socket
import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client
import os
import signal
import atexit

class Mechoscore:
    '''
    Mechoscore containts and xmlrpc server that nodes, publishers,
    subscribers register to in order to hop on the mechos network.
    '''

    def __init__(self, ip="127.0.0.1", port=5959):
        '''
        Initialize the XMLRPCServer.

        Parameters:
            ip: The ip address to host the XMLRPCServer. Default "http://127.0.0.101"
            port: The port to host the XMLRPCServer. Default 8000

        Returns:
            N/A
        '''
        self.xmlrpc_server = SimpleXMLRPCServer((ip,port), logRequests=False)

        #Register functions that nodes will call to register themselves as well
        #as there publishers and subscribers.
        self.xmlrpc_server.register_function(self.register_node)
        self.xmlrpc_server.register_function(self.unregister_node)
        self.xmlrpc_server.register_function(self.register_publisher)
        self.xmlrpc_server.register_function(self.register_subscriber)

        self.node_information = {}

        #When a new node is created, a client to that nodes xml rpc will be created.
        self.xmlrpc_clients_to_nodes = {}

        #At the exit of the mechoscore, unregister and kill all nodes if any are running.
        atexit.register(self.unregister_all_nodes)

    def register_node(self, name, pid, xmlrpc_server_ip, xmlrpc_server_port):
        '''
        Register a node with mechoscore. Check if that node is already created.
        If it is already created, send an error message and do not let it connect.

        Parameters:
            node_name: The name of the node to be created.
            pid: The process id of the node.

        Returns:
            True: If the node can be created.
            False: If the node name already exists, then it cant be created.
        '''
        if(name in self.node_information.keys()):
            return False

        #Create an xmlrpc client to the newly registered node.
        self.xmlrpc_clients_to_nodes[name] = xmlrpc.client.ServerProxy("http://" + \
                    xmlrpc_server_ip + ":" + \
                    str(xmlrpc_server_port))

        self.node_information[name] = {"pid":pid,
                                                    "xmlrpc_server_ip": xmlrpc_server_ip,
                                                    "xmlrpc_server_port":xmlrpc_server_port,
                                                    "publishers":{},
                                                    "subscribers":{}}
        print("[INFO]: Registering Node %s to the mechos network" % name)
        return True

    def unregister_all_nodes(self):
        '''
        Unregister and kill all nodes in the mechos network

        Parameters:
            N/A
        Returns:
            N/A
        '''
        print("[WARNING]: Unregistering all Node from mechos network")
        node_names = list(self.node_information.keys()).copy()
        for node_name in node_names:
            self.unregister_node(node_name)

    def unregister_node(self, name):
        '''
        Unregister a node with mechoscore. Before a node is killed, it should
        call this in order to unregister it. Also kill the node.

        Parameters:
            node_name: The name of the node to unregister.
        Returns:
            N/A
        '''

        #Remove the information about a node.
        node_information = self.node_information[name]


        #Kill the publisher of the nodes
        for publisher_id in node_information["publishers"].keys():

            for node_name in self.node_information.keys():

                for subscriber_id in self.node_information[node_name]["subscribers"].keys():

                    self.xmlrpc_clients_to_nodes[node_name]._kill_subscriber_connection(publisher_id)

            self.xmlrpc_clients_to_nodes[name]._kill_publisher(publisher_id)

        for subscriber_id in node_information["subscribers"].keys():
            self.xmlrpc_clients_to_nodes[name]._kill_subscriber(subscriber_id)

        self.node_information.pop(name)
        #Kill the process the node is running in.
        print("[WARNING]: Unregistering and killing the process continaing Node %s" % name)
        os.kill(node_information["pid"], signal.SIGTERM)

        return(True)
    def register_publisher(self, node_name, id, topic, ip, port, protocol):
        '''
        Register a publisher from a node. Check if the publisher has an allowable
        ip and port.

        Parameters:
            node_name: The name of the node registering the publisher
            id: The unique id of the publisher
            topic: The topic name that the publisher will publish data to.
            ip: The ip address that the publisher want to send on.
            port: The port that the publisher wants to send on.
            protocol: Either tcp or udp.
        '''

        self.node_information[node_name]["publishers"] = {id:{"topic":topic,
                                                         "ip":ip,
                                                         "port":port,
                                                         "protocol":protocol}}

        self.new_publisher_update_connections(node_name, id)
        print("[INFO]: Registering publisher with topic %s on Node %s" % (topic, node_name))
        return True



    def register_subscriber(self, node_name, id, topic, ip, port, protocol):
        '''
        Register a subscriber from a node. This will allow the subscriber to get
        updates on when to connect to publishers and the ports they need to connect to.

        Parameters:
            node_name: The name of the node registering the subscriber.
            topic: The topic name that the subscriber will subscribe to get data from.
            protocol: Either udp or tcp.
        '''
        self.node_information[node_name]["subscribers"] = {id:{"topic":topic,
                                                                "ip":ip,
                                                                "port":port,
                                                                "protocol":protocol}}
        print("[INFO]: Registering subscriber with topic %s on Node %s" % (topic, node_name))
        self.new_subscriber_update_connections(node_name, id)
        return(True)


    def new_subscriber_update_connections(self, node_name, subscriber_id):
        '''
        If a new subscriber of publisher comes onto the network, connect it with its counter
        parts.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        xmlrpc_client_to_subscriber_node = self.xmlrpc_clients_to_nodes[node_name]
        subscriber_topic = self.node_information[node_name]["subscribers"][subscriber_id]["topic"]
        subscriber_protocol =  self.node_information[node_name]["subscribers"][subscriber_id]["protocol"]
        subscriber_ip = self.node_information[node_name]["subscribers"][subscriber_id]["ip"]
        subscriber_port = self.node_information[node_name]["subscribers"][subscriber_id]["port"]
        #Iterate through each nodes publishers, and connect it to the repectable topics
        for nodes in self.node_information.keys():

            for publisher_id in self.node_information[nodes]["publishers"].keys():

                #publisher topics of current node.
                publisher_topic = self.node_information[nodes]["publishers"][publisher_id]["topic"]
                publisher_ip = self.node_information[nodes]["publishers"][publisher_id]["ip"]
                publisher_port = self.node_information[nodes]["publishers"][publisher_id]["port"]
                publisher_protocol = self.node_information[nodes]["publishers"][publisher_id]["protocol"]

                xmlrpc_client_to_publisher_node = self.xmlrpc_clients_to_nodes[nodes]

                if(publisher_topic == subscriber_topic and publisher_protocol == subscriber_protocol):
                    xmlrpc_client_to_subscriber_node._update_subscriber(subscriber_id, publisher_id, publisher_ip, publisher_port)
                    xmlrpc_client_to_publisher_node._update_publisher(publisher_id, subscriber_id, subscriber_ip, subscriber_port)

    def new_publisher_update_connections(self, node_name, publisher_id):
        '''
        If a new publisher comes onto the network, tell the subscriber of the topic
        to connect.

        Parameters:
            node_name:
            publisher_id: The unique publisher id.
        Returns:
            N/A
        '''
        xmlrpc_client_to_publisher_node = self.xmlrpc_clients_to_nodes[node_name]
        publisher_topic = self.node_information[node_name]["publishers"][publisher_id]["topic"]
        publisher_ip = self.node_information[node_name]["publishers"][publisher_id]["ip"]
        publisher_port = self.node_information[node_name]["publishers"][publisher_id]["port"]
        publisher_protocol = self.node_information[node_name]["publishers"][publisher_id]["protocol"]

        for nodes in self.node_information.keys():

            for subscriber_id in self.node_information[nodes]["subscribers"].keys():

                #publisher topics of current node.
                subscriber_topic = self.node_information[nodes]["subscribers"][subscriber_id]["topic"]
                subscriber_protocol = self.node_information[nodes]["subscribers"][subscriber_id]["protocol"]
                subscriber_ip = self.node_information[nodes]["subscribers"][subscriber_id]["ip"]
                subscriber_port = self.node_information[nodes]["subscribers"][subscriber_id]["port"]

                xmlrpc_client_to_subscriber_node = self.xmlrpc_clients_to_nodes[nodes]

                if(publisher_topic == subscriber_topic and publisher_protocol == subscriber_protocol):
                    xmlrpc_client_to_subscriber_node._update_subscriber(subscriber_id, publisher_id, publisher_ip, publisher_port)
                    xmlrpc_client_to_publisher_node._update_publisher(publisher_id, subscriber_id, subscriber_ip, subscriber_port)

    def run(self):
        '''
        Run the mechoscore server.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        self.xmlrpc_server.serve_forever()

if __name__ == "__main__":
    mechoscore_server = Mechoscore()
    mechoscore_server.run()

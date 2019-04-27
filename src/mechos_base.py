import abc

class Node(abc.ABCMeta):

    def __init__(self, node_name, device_connection='tcp://127.0.0.101',
                    node_connection_port="5558"):
        __metaclass = abc.ABCMeta

    @abc.abstractmethod
    def _connect_node_to_mechoscore(self):
        pass;

    @abc.abstractmethod
    def create_publisher(self, topic, pub_port="5559"):

        '''
            Return
            -----------------------------------------
            Publisher           : Using Publisher Class

        '''

        return new_pub

    @abc.abstractmethod
    def create_subscriber(self, topic, callback, timeout=.01, sub_port="5560"):

        '''
            Method to Create Subscriber and return Subscriber
        '''

        #TODO: Have node store information about newly created subscribers

        #register new subscription to subscription _sub_poller

        return new_sub

    @abc.abstractmethod
    def spinOnce(self, specific_subscriber = None, timeout=0.001):
        '''
        Attempt to retrieve a message from each subscriber and pass message to
        respective callback. Currently this is a single thread.

        Parameters:
            specific_subscriber: If none, then spinOnce will listen for all
                                subsriber messages. Else, pass a subsriber object
                                to only look for message to that subscriber.
            timeout: Time to wait for polling messages before continuing. T
        Returns:
            N/A
        '''

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
            tcp://127.0.0.101:5559. Note initialization of an object of this class
            should only be done by the node class through the create_publisher()
            function.

            Parameters:
                topic: A well-defined topic name to publish messages to
                pub_context: The zmq context to keep control of all the
                            publishers in the node.
                device_connection: The TCP IP address to connect to. Default is
                                    tcp://127.0.0.101
                pub_port: The tcp socket to connect the publisher socket to.
            '''




        @abc.abstractmethod
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
        @abc.abstractmethod
        def _spinOnce(self):
            '''
            Receive a single message into subscriber and pass message to the
            subscribers given callback.

            Parameters:
                N/A
            Returns:
                N/A
            '''

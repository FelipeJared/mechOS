import socket
import threading
import time

# Classes
from NodeClass import Node

class NetworkNode(Node):
    def __init__(self, HOST, TOPIC, TYPE):
        '''
            PARAMETERS

            -------------------------------------------------------------------------------------------------
        '''

        self._HOST              = HOST
        self._DOMAIN            = socket.AF_INET  #IPV4 ALWAYS
        self._TOPIC             = TOPIC

        self._PUBLISHERS        = {}  # KEY: PORT | VALUE: PUB
        self._SUBSCRIBERS       = {}  # KEY: PORT | VALUE: LIST(SUB)

    def get_publisher(self, PORT):
        try:
            return self._PUBLISHERS[PORT]

        except KeyError:
            print("Publisher Does Not Exist")

    def get_subscriber(self, PORT):
        try:
            return self._SUBSCRIBERS[PORT]
        except KeyError:
            print("Subscriber Does Not Exist")

    def add_publisher(self, PORT, TYPE=None, PUBRATE=None):
        self._PUBLISHERS[PORT] = PubClass.Publisher(self._HOST, PORT, self._TOPIC, PUBRATE)
        if TYPE is not None:
            self._PUBLISHERS[PORT].setType(TYPE)

    def add_subscriber(self, PORT, TYPE=None, SUBRATE=None):
        self._SUBSCRIBERS[PORT] = SubClass.Subscriber(self._HOST, PORT, self._TOPIC, SUBRATE)
        if TYPE is not None:
            self._SUBSCRIBERS[PORT].setType(TYPE)

    def delete_publisher(self, PORT):
        del self.PUBLISHERS[PORT]

    def delete_subscriber(self, PORT):
        del self.SUBSCRIBER[PORT]

    def initializePublishers(self, LIST):
        # Where list is a List of Publishers to initialize

        '''
        for pub in LIST:
            if (pub in self.PUBLISHERS.keys())
                self.PUBLISHERS.keys(pub).start()
        '''
        pass

    def initializePublishers(self):
        ''' This will be the initialize function for PubHandler
        for pub in PUBLISHERS.value():

            pub.start()
        '''
        pass
    def deinitializePublishers(self):
        ''' This will be the deinitialize function for PubHandler:

        for pub in Publishers
        '''
        pass

    def run(self):
        while(True):
            for PUB in self._PUBLISHERS.values():
                if ((PUB._timeAtLastPublish is None) or (time.time() - PUB._timeAtLastPublish >= PUB._pubRate)):
                    PUB.publish()
            for SUB in self._SUBSCRIBERS.values():
                if ((SUB._timeAtLastSubscribe is None) or (time.time() - SUB._timeAtLastSubscribe >= SUB._subRate)):
                    SUB.subscribe()

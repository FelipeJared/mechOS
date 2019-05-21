from mechos_socket_version import Node
import socket
import threading
import json

class god_node:

    def __init__(self, port=5559):
        #TODO: overwrite original node init method. initialize differently, with threads
        i = 0
        god_Node = Node("God Node", self.port)
        with open('Nodelist.json') as json_file:
            data = json.load(json_file)
            for p in data['Node']:
                god_Node.create_publisher(p['Topic'], p['Connection'],


    class Control:
        def __init__(self):
            '''
            Todo: Initialize threads here, publisher and subscriber threads.
            '''
            pass
        def connect(pub, sub, port):
            '''
            Todo: creates a connection between a publsiher, subscriber at certain port
            If no publisher specified, create a publisher at that port, and initialize that conection
            '''
            pass

        def disconnect(sub, port):
            '''
            Todo: disconnect subscriber from port by using python's del keyword
            '''
            pass

        def getMap():
            '''
            Initialize a map, output to user complete map of all publishers and subscribers
            '''
            pass

        def findPub(port):
            pass
    def run(self):
        pass

if __name__ == '__main__':
    run()

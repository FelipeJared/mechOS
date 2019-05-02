import socket
import mechos_socket_version as msv
import time

def main():
    node = msv.Node("Random topic")
    pub = node.create_publisher("Topic chatter")
    while(True):
        pub.publish("Hello World")
        time.sleep(0.01)

if __name__ == '__main__':
    main()

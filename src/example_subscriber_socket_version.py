import mechos_socket_version as msv
import socket
import time

def main():
    node = msv.Node("Random topic")
    sub = node.create_subscriber("Topic listener")
    while(True):
        sub.subscribe()
        time.sleep(0.5)

if __name__ == '__main__':
    main()

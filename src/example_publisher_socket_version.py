import socket
import mechos_socket_version as msv
import time

def main():
    count = 0
    node = msv.Node("Random topic")
    pub = node.create_publisher("Topic chatter")
    start = time.time()
    try:
        while(True):
            pub.publish("Hello World")
            count = count + 1
            time.sleep(0.01)
    except KeyboardInterrupt:
        end = time.time()
        print(count/(end - start))

if __name__ == '__main__':
    main()

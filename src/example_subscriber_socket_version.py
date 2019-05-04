import mechos_socket_version as msv
import socket
import time

def main():
    count = 0
    node = msv.Node("Random topic", 'udp://127.0.0.101', 5556)
    sub = node.create_subscriber("Topic listener", 5560)
    start = time.time()
    try:
        while(True):
            sub.subscribe()
            count = count + 1
            #time.sleep(0.5)
    except:
        end = time.time()
        print(count/(end - start))

if __name__ == '__main__':
    main()

import zmq
from zmq.devices.basedevice import ProcessDevice
import mechos
from multiprocessing import Process
import sys
import time

def mechoscore_main():
    '''
    Mechoscore handles communication between nodes through multiple message
    "routing" processes. Mechoscore is "master" node, which all other nodes
    must connect to in order to communicate.

    Parameters:
        N/A
    Returns:
        N/A
    '''
    #TODO: Create pair (client/server) to connect mechoscore to nodes

    # start publisher/subscriber handler process
    pub_sub_process_handler = pub_sub_handler()

    #TODO: Add monitoring functionalities in main loop once nodes are implemented

    try:
        while(1):
            time.sleep(0.1) #do nothing
    except KeyboardInterrupt:
        print("Ctrl-C causes mechoscore to shutdown")
    finally:
        print("Closing down mechoscore")
        sys.exit()

def pub_sub_handler():
    '''
    Communication link for publisher/subscribers. Utilize zmq devices to
    automatically route publisher messages to subscribers of the same topic
    name.

    Parameters:
        N/A
    Returns:
        N/A
    '''
    pub_connection_socket = "tcp://127.0.0.101:5559"
    sub_connection_socket = "tcp://127.0.0.101:5560"

    #create a zmq device to connect routes pub/sub messages
    pub_sub_handler_device = ProcessDevice(zmq.FORWARDER, zmq.SUB, zmq.PUB)
    pub_sub_handler_device.bind_in(pub_connection_socket)
    pub_sub_handler_device.bind_out(sub_connection_socket)
    pub_sub_handler_device.setsockopt_in(zmq.SUBSCRIBE, "".encode("utf-8"))
    pub_sub_handler_device.start()

    #return the process handler for the pub_sub to control when to close it
    return pub_sub_handler_device

if __name__ == "__main__":
    mechoscore_main()

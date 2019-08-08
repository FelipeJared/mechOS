from MechOS import mechos
import time
from MechOS.simple_messages.float_array import Float_Array
from MechOS.simple_messages.bool import Bool

def chatter_callback(chatter_message):
    '''
    Callback function for subscriber to pass data into. All subscribers use
    callback functions to pass their recieved data to.

    Parameters:
        chatter_message: The data recieved over topic chatter from publisher. Each
        time a spinOnce is called, the data being sent from the publisher is
        inserted here.
    '''
    print("Message received:",chatter_message)

def listener():
    '''
    Example of a subsriber subscribing to topic "chatter"
    '''
    #initializes a node called listener
    listener_node = mechos.Node("listener", node_ip="127.0.0.1", mechoscore_ip="127.0.0.1")

    #create a subscriber to subscribe to topic chatter.
    #Since the publisher chatter sends a message format
    #Float_Array(4), make the subscriber receive the same
    #format.

    #The third parameter is the callback function to pass the data
    #into once it is received. It will pass the data as the first
    #parameter.
    sub = listener_node.create_subscriber("chatter", Float_Array(4), chatter_callback, protocol="tcp")

    while(1):

        #Spin once will check ALL the subscriber registered to this node
        #to see if they have messages.
        listener_node.spin_once()
        time.sleep(0.01)


if __name__ == "__main__":
    listener()

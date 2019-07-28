from MechOS import mechos
import time
from MechOS.simple_messages.float_array import Float_Array
from MechOS.simple_messages.bool import Bool
def chatter_callback(chatter_data):
    '''
    Callback function for subscriber to pass data into.

    Parameters:
        chatter_data: The data recieved over topic chatter from publisher. Each
        time a spinOnce is called, the data being sent from the publisher is
        inserted here.
    '''
    print('1', chatter_data)

def chatter_callback_2(chatter_data):
    print('2', chatter_data)

def listener():
    '''
    Example of a subsriber subscribing to topic "chatter"
    '''
    #initializes a node called listener
    listener_node = mechos.Node("listener")

    #create a subscriber to subscribe to topic chatter
    sub = listener_node.create_subscriber("chatter_2", Bool(), chatter_callback, protocol="tcp")
    print(sub.id)
    sub_2 = listener_node.create_subscriber("chatter_2", Bool(), chatter_callback_2, protocol="tcp")
    print(sub_2.id)


    while(1):

        listener_node.spin_once()
        time.sleep(0.01)


if __name__ == "__main__":
    listener()

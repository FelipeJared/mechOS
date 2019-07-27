from MechOS import mechos
import time
from MechOS.simple_messages.float_array import Float_Array

def talker():
    '''
    Example of publishing continuous data to topic "chatter"
    '''
    #initializes a node called talker
    talker_node = mechos.Node("talker")

    #create a tcp publisher to publish to topic chatter

    pub = talker_node.create_publisher("chatter",Float_Array(4), protocol="udp")
    message = [0.12, 1.65, 192.3, 10]
    while(1):

        #publish message to chatter (must be encoded as type bytes)
        pub.publish(message)
        time.sleep(0.01)

if __name__ == "__main__":
    talker()

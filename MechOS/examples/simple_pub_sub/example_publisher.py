from MechOS import mechos
import time
from MechOS.simple_messages.float_array import Float_Array
from MechOS.simple_messages.bool import Bool

def talker():
    '''
    Example of publishing continuous data to topic "chatter"
    '''
    #initializes a node called talker. The first parameter is the name you
    #would like to give this node. Node ip is the ip address that you want
    #this node (executable) to run. mechoscore_ip is the ip address that
    #the mechoscore server is running on.
    talker_node = mechos.Node("talker", node_ip="127.0.0.1", mechoscore_ip="127.0.0.1")

    #create a tcp publisher to publish to topic chatter
    #The first parameter is the topic name that the publisher
    #should publish data to. If any subscribers subscrib to this topic AND
    #have the same protocol, the mechsocore will connect the publisher and
    #subscriber together.

    #The second parameter is an object that describes the message format being sent.
    #In this example a Float Array (list) containing 4 floats. This will be the message format
    #of the messages that can be sent. This object will automatically pack and unpack the
    #data. NOTE: You can also create your own custom message formats using the message format
    #template.

    #The protocol is the socket protocol to send messages over. This can either
    #be tcp or udp.
    pub = talker_node.create_publisher("chatter", Float_Array(4), protocol="tcp")

    #Some random message to send (4 floats)
    message = [0.12, 1.65, 192.3, 10]
    while(1):

        #publish message to chatter
        pub.publish(message)
        time.sleep(0.01)

if __name__ == "__main__":
    talker()

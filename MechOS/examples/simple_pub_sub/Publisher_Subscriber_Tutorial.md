# 1 Writing Publisher and Subscriber Nodes in MechOS
In MechOS, a node is a representation/executable of an independent sub-system in a larger network of node sub-systems that communicate to one another to make up a full, modular system . The nodes in the MechOS network communicate to each other via a publisher/subscriber based protocol. With this communication scheme, this systems has the ability to perform one-to-one, one-to-many, many-to-one, and many-to-many communication. The system also automatically handles nodes dynamically connecting and disconnecting from the overall network, without having other nodes fail. Lastly, the system even supports multi-machine communication for applications of distributed computing.

## 1.1 Publishers
Publishers are created under a node, and as many publishers as desire can be created under a node. The role of publishers is to publish (or emit) data to the network. Each publisher is given a **topic name** that signifies the type of data that publisher is publishing. Any subscribers in the network that match with the same topic name of a publisher will receive the messages the publisher emits.

## 1.2 Subscribers

Subscribers subscribe to a topic. If a publisher is publishing messages to the same topic name of a subscriber, then the subscriber will receive the message and pass it to a designated callback function.

# 2 Code-Writing a Publisher
The code below is an example of script containing a single MechOS node named "talker" with a single publisher that publishes to topic "chatter".

```python
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

```

## 2.1 The Code Explained

Lets break down the code.
```python
from MechOS import mechos
```
MechOS must be imported to use its AMAZING communication abilities (HINT: How to become a Ninja).
```python
talker_node = mechos.Node("talker", node_ip="127.0.0.1", mechoscore_ip="127.0.0.1")
pub = talker_node.create_publisher("chatter", Float_Array(4), protocol="tcp")
```
To begin any sort of communication with publishers and subscribers, a MechOS node must be declared with a unique name provided. This node will register with mechoscore to provide information on the node such as the publishers and subscribers registered to the node.

A publisher is created under the node. The publisher publishes messages to topic chatter, and messages have type format Float_Array(4), which means send a list containing 4 floats.

# 3 Code-Writing a Subscriber

The code below is an example of a MechOS node name "listener" that has a subscriber listening to topic "chatter".
```python
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
    listener_node = mechos.Node("listener", node_ip="127.0.0.1",mechoscore_ip="127.0.0.1")

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
```
## 3.1 The Code Explained
```python
def chatter_callback(chatter_message):
    print(chatter_message)
```
Subscribers use callback functions to route data when it is read from the master communication node MechOSCore. The data always be passed as the first parameter. In this example, the data received is simply printed out.

```python
 listener_node = mechos.Node("listener", node_ip="127.0.0.1",mechoscore_ip="127.0.0.1")
sub = listener_node.create_subscriber("chatter", Float_Array(4), chatter_callback, protocol="tcp")
```

Declare a MechOS node named listener. Create on subscriber to topic "chatter" and place the data as the first parameter to the function chatter_callback.

```python
while(1):

        #Spin once will check ALL the subscriber registered to this node
        #to see if they have messages.
        listener_node.spin_once()
        time.sleep(0.01)
```
To actually poll the message received to the subscriber, call the nodes spinOnce function. If the subscribers object is passed as a parameter, then only a message for that subsriber will be polled. If no parameters are passed, then all subscribers will be polled for messages.

# 4 Running your First MechOS Program!

To acutally run a MechOS program, the `MechOS.mechoscore.py` script needs to be running in its own process to let nodes communicate with each other. Simply open up a terminal and execute this scripts.

```
Terminal 1:

python -m MechOS.mechoscore
```
```
Terminal 2:

python example_subscriber.py
```
```
Terminal 3:

python example_publisher.py
```
And there you have it, you have just completed your first MechOS program!!!


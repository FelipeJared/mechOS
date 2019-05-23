import mechos
import time

def talker():
    '''
    Example of publishing continuous data to topic "chatter"
    '''
    #initializes a node called talker
    count = 0
    talker_node = mechos.Node("talker")

    #create a publisher to publish to topic chatter
    pub = talker_node.create_publisher("chatter")
    start = time.time()
    try:
        while(1):

        #publish message to chatter (must be encoded as string)
            pub.publish("Hello World")
            count = count + 1
            #time.sleep(0.01)
    except:
        end = time.time()
        print(count/(end - start))

if __name__ == "__main__":
    talker()

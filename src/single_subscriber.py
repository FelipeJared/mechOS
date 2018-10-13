import mechos
import time

def ahrs_callback(data):
    print(data)
def dvl_callback(data):
    print(data)

if __name__ == "__main__":

    subscriber_node = mechos.Node("ahrs_receiver")
    sub = subscriber_node.create_subscriber("ahrs_data", ahrs_callback)
    sub2 = subscriber_node.create_subscriber("dvl_data", dvl_callback)
    #sub.start_subscription()
    while(1):
        #will get a single message from all subscribers in node
        #data will be passed to respective callback function
        subscriber_node.spinOnce()

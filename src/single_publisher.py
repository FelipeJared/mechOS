import mechos
import time
import sys


if __name__ == "__main__":
    topic = "ahrs_data"
    message = "101"
    node = mechos.Node("ahrs")
    ahrs_pub = node.create_publisher(topic)
    dvl_pub = node.create_publisher("dvl_data")
    while(1):
        ahrs_pub.publish(message)
        dvl_pub.publish("ping")
        time.sleep(0.01)

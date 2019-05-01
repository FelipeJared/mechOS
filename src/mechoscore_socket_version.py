import socket
import sys
import time
import argparse
from thread import *

class _Pub_Sub_Handler:

    def __init__(self, device_connection = None, port = None):

        if device_connection is None:
            device_connection = "udp://127.0.0.101" #Different from mechos, because we might be using udp as well
        if port is None:
            port = 5559

        self.device_connection = device_connection
        self.port = port

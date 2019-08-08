'''
'''
import struct

class Int:
    '''
    '''
    def __init__(self):
        '''
        '''
        #construct the message format
        self.message_constructor = 'i'
        #number of bytes for this message
        self.size = 4

    def _pack(self, message):
        '''
        '''
        encoded_message = struct.pack(self.message_constructor, message)
        return(encoded_message)

    def _unpack(self, encoded_message):
        '''
        '''
        message = struct.unpack(self.message_constructor, encoded_message)[0]
        return(message)

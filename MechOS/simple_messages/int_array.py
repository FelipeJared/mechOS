'''
'''
import struct

class Int_Array:
    '''
    '''
    def __init__(self, number_of_ints):
        '''
        '''
        #construct the message format
        self.message_constructor = ''
        for i in range(number_of_ints):
            self.message_constructor += 'i'

        #number of bytes for this message
        self.size = 4 * number_of_ints

    def _pack(self, message):
        '''
        '''
        encoded_message = struct.pack(self.message_constructor, *message)
        return(encoded_message)

    def _unpack(self, encoded_message):
        '''
        '''
        message = struct.unpack(self.message_constructor, encoded_message)
        return(message)

import io

class IOhandler:
    '''
    The reader class is meant to read messages (duh).
    '''
    def __init__(self, buffer, message_dict = None):
        self._buffer = buffer
        self._list = []
        self._byteArray = None
        if message_dict is None:
            self._dictionary = {}
        self._dictionary = message_dict

    def read(self, flag, value):
        if flag is "buff":
            self._byteArray = self._buffer.read(value)
            return self._byteArray
        else:
            return self._dictionary[value]

    def readAll(self, flag):
        if flag is "buff":
            return self._buffer.getvalue()
        else:
            return self._dictionary

    def read_from_file(self, flag, file):
        with open(file, flag) as f:
            for line in f:
                self._list.append(line)
        return self._list

    def get_buffer(self):
        return self._buffer

    def write(self, flag, message = None):
        if flag is buff:
            if message is None:
                message = self._buffer.getvalue()
                with self._buffer as f:
                    print(f.write(message))
        else:
            length = len(self._dictionary) + 1
            self._dictionary[length] = message

    def write_to_file(self, flag, file, message = None):
        with open(file, flag) as f:
            f.write(message)

    #def seek(self, message):

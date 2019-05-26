import io

class Reader:
    '''
    The reader class is meant to read messages (duh).
    '''
    def __init__(self, message, buffer = None):
        if buffer is None:
            self._buffer = io.BytesIO(message)
        else:
            self._buffer = buffer
        self.list = []

    def read(self, size = None):
        byteArray = self._buffer.read(size)
        while True:
            print(byteArray)

    def readAll(self):
        while True:
            print(self._buffer.getvalue())

    def read_from_file(self, file):
        with open(file, "br") as self._buffer:
            for line in self._buffer:
                self.list.append(line)
        return self.list

    #def seek(self, message):

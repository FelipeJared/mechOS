import io

class Reader:
    '''
    The reader class is meant to read messages (duh).
    '''
    def __init__(self, mem_location = None):
        if(mem_location is None):
            self._buffer = io.BytesIO()
        else:
            try:
                self._buffer = io.BytesIO(mem_location)
            except AttributeError:
                print("Not a valid memory location")

        self.list = []

    def read(self, size = None):
        while True:
            self._buffer.read(size)

    def readAll(self):
        self._buffer.getvalue()

    def read_from_file(self, file):
        with open(file, "br") as self._buffer:
            for line in self._buffer:
                self.list.append(line)
        return self.list

    #def seek(self, message):

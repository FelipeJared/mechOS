import io

class Writer:
    '''
    This might come as a shock, but we use the writer class to write messages.
    '''
    def __init__(self, mem_location = None, message = None):
        if(mem_location is None):
            self._buffer = io.BytesIO()
        else:
            try:
                self._buffer = io.BytesIO(mem_location)
            except AttributeError:
                print("Not a valid memory location")

        if message is not None:
            self._message = message

    def write(self, message = None, continuous = False):
        if message is None:
            message = self._message

        with self._buffer as f:
            while True:
                f.write(message)

    def write_to_file(self, file, message = None):
        if message is None:
            message = self._message
        with open(file,"bw") as self._buffer:
            self._buffer.write(message)

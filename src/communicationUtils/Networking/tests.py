from Writer import Writer as WriteClass
from Reader import Reader as ReadClass
import io

#writer.write("Hey") throws errors
#writer.write()
#writer.write_to_file("tests.txt", b"Chelsea sucks")


buffer = io.BytesIO(b"Hi, my name is Shafi, and I want this program to work. That would be nice")
writer = WriteClass(b"message", buffer)
writer.write(b"Hey")
#reader = ReadClass(b"Hello", buffer)
#print(reader.read(32))

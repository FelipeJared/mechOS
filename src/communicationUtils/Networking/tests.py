from Writer import Writer as WriteClass
from Reader import Reader as ReadClass

#writer = WriteClass(b"12", b"Hello World")
#writer.write("Hey") throws errors
#writer.write()
#writer.write_to_file("tests.txt", b"Chelsea sucks")

reader = ReadClass(b"yo")
#reader.read(10)
my_list = reader.read_from_file("tests.txt")
for x in my_list:
    print(x)

from NodeClass import Node
import io
import threading
import glob
from PIL import Image, ImageDraw

class camera_node(Node):
    def run(self, pic):
        pic.save(self.get_reader().get_buffer(), format ='jpeg')

class receiver_node(Node):
    def run(self):
        return self.get_reader().readAll("buff")

def list_pics(file_path):
    pic_list = []
    for filename in glob.glob(file_path):
        image = Image.open(filename)
        pic_list.append(image)
    return pic_list

def main():
    #buffer = io.BytesIO()
    pictures = list_pics('input_pics/*.jpg')
    cam_node = camera_node('udp://127.0.0.101', 'imagetest', 'udp')
    #cam_node.add_reader(buffer)
    rnode = receiver_node('udp://127.0.0.101', 'imagetest', 'udp')
    #rnode.add_reader(buffer)
    num = 1
    for picture in pictures:
        buffer = io.BytesIO()
        cam_node.add_reader(buffer)
        cam_node.run(picture)
        rnode.add_reader(cam_node.get_reader().get_buffer())
        new_pic = Image.open(io.BytesIO(rnode.run()))
        new_draw = ImageDraw.Draw(new_pic)
        new_pic.save(("output_pics/output {}".format(num)), format='png')
        num += 1
        del(buffer)

if __name__ == '__main__':
    main()

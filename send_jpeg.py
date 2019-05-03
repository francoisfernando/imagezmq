

# run this program on each RPi to send a labelled image stream
import socket
import time
from picamutil import PiJpegStream
import imagezmq.imagezmq as imagezmq
import cv2
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-H", "--hub", required=True,
    help="image hub ip address or host name")
args = vars(ap.parse_args())

hub_host = args["hub"]
hub_host_url = 'tcp://{}:5555'.format(hub_host)
print('hub host: {}'.format(hub_host_url))
sender = imagezmq.ImageSender(connect_to=hub_host_url)

rpi_name = socket.gethostname() # send RPi hostname with each image
picam = PiJpegStream(resolution=(640, 480), framerate=16).start()
time.sleep(2.0)  # allow camera sensor to warm up

avg_time_to_send = None

while True:  # send images as stream until Ctrl-C
    s = time.time()
    image = picam.read()
    print('read {} bytes image in {} s'.format(len(image), time.time()-s))
    s = time.time()
    sender.send_jpg(rpi_name, image)
    time_to_send = time.time()-s
    avg_time_to_send = time_to_send if avg_time_to_send is None else (avg_time_to_send + time_to_send) / 2
    print('sent image in {} s'.format(avg_time_to_send))
    time.sleep(0.05)

picam.close()


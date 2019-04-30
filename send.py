
# run this program on each RPi to send a labelled image stream
import socket
import time
from imutils.video import VideoStream
import imagezmq.imagezmq as imagezmq
import cv2
import numpy as np

sender = imagezmq.ImageSender(connect_to='tcp://192.168.10.183:5555')

rpi_name = socket.gethostname() # send RPi hostname with each image
picam = VideoStream(usePiCamera=True).start()
time.sleep(2.0)  # allow camera sensor to warm up

avg_image = None

while True:  # send images as stream until Ctrl-C
    s = time.time()
    image = picam.read()
    print('read {} byte  {} array image in {} s'.format(image.size * image.itemsize, image.shape, time.time()-s))
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #gray_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    if avg_image is None:
        avg_image = gray_image.copy().astype('float')
        continue
    else:
        # add gray image to weighted average image
        cv2.accumulateWeighted(gray_image, avg_image, 0.5)
        diff = cv2.absdiff(gray_image, cv2.convertScaleAbs(avg_image))
        # threshold the frame delta image and dilate the thresholded image

        thresh = np.mean(diff)
        lt_count = (diff < thresh).sum()
        gt_count = (diff > thresh).sum()
        print('diff thresh: {}, lt_count: {}, gt_count: {}'.format(thresh, lt_count, gt_count))

    print('gray image {} byte'.format(gray_image.size * gray_image.itemsize))
    s = time.time()
    sender.send_image(rpi_name, gray_image)
    print('sent image in {} s'.format(time.time()-s))
    time.sleep(5.0)


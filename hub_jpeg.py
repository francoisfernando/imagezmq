# run this program on the Mac to display image streams from multiple RPis
import cv2
import numpy as np
import imagezmq.imagezmq as imagezmq
image_hub = imagezmq.ImageHub()

while True:  # show streamed images until Ctrl-C
    rpi_name, jpeg_bytes = image_hub.recv_jpg()
    jpeg_image = np.asarray(jpeg_bytes, dtype="uint8")
    image = cv2.imdecode(jpeg_image, cv2.IMREAD_COLOR)
    cv2.imshow(rpi_name, image) # 1 window for each RPi
    cv2.waitKey(1)
    image_hub.send_reply(b'OK')

#!/usr/bin/env python
import signal
import time
import os
import datetime

import cv2
import scipy.misc
import numpy as np
from multiprocessing import Process, Queue
import pyfreenect2

"""
Config section
"""
# Folder where to store data
REPO_HOME = "/Users/sebastian/Projects/food3d/"
# Dump interval in frames
DUMP_INTERVAL = 1
# Cropping sizes
h = 480
w = 640

def disk_writer():
    """
    Write data to disk async via our threadsafe queue
    """
    while(True):
        data = q.get(block=True)
        color_frame, depth_frame = data

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S_%f')
        st = "kinectv2_" + st

        np.save(REPO_HOME + "/" + st + "_depth.npy", depth_frame)
        np.save(REPO_HOME + "/" + st + "_bgr.npy", color_frame)


"""
Start main program
"""
# Initialize device
serialNumber = pyfreenect2.getDefaultDeviceSerialNumber()
kinect = pyfreenect2.Freenect2Device(serialNumber, pyfreenect2.USE_OPENGL_PACKET_PIPELINE)

# Set up frame listener
frameListener = pyfreenect2.SyncMultiFrameListener(pyfreenect2.Frame.COLOR, pyfreenect2.Frame.IR, pyfreenect2.Frame.DEPTH)
kinect.setColorFrameListener(frameListener)
kinect.setIrAndDepthFrameListener(frameListener)

# Start recording
kinect.start()

# Print useful info
print "Kinect serial: %s" % kinect.serial_number
print "Kinect firmware: %s" % kinect.firmware_version

registration = pyfreenect2.Registration(kinect)

# Initialize OpenCV stuff
cv2.namedWindow("RGB")
cv2.namedWindow("Depth")
cv2.startWindowThread()

# Create a threadsafe queue to dump data async
q = Queue()

# Spawn the disk writer daemon
p = Process(target=disk_writer)
p.daemon = True
p.start()

# Main loop starts here
idx  = 0
toggle = False
while 1:
    frames = frameListener.waitForNewFrame()

    # Grab a framepair for registration
    rgbFrame = frames.getFrame(pyfreenect2.Frame.COLOR)
    depthFrame = frames.getFrame(pyfreenect2.Frame.DEPTH)

    (undistorted,registered, bigdepth) = registration.apply(rgbFrame=rgbFrame, depthFrame=depthFrame)

    depth_frame = bigdepth.getDepthData()

    # Crop out patches of the mapped depth image. This is necessary because the RGB
    # camera has a wider field of view than the depth sensor
    cy, cx = (depth_frame.shape[0] - h)/2 , (depth_frame.shape[1] - w)/2
    depth_frame = depth_frame[cy:cy+h,cx:cx+w]
    # Crop the same piece out of the color image
    # Attention, this is BGR here for rendering convenience (no need to transform to RGB)
    color_frame = rgbFrame.getBGRData()
    # Crop as well
    color_frame = color_frame[cy:cy+h,cx:cx+w]

    # Make the depth appear nice (may cost some performance here)
    dmin = 0.0
    dmax = 3000.0   # 3m
    s = 255.0/(dmax - dmin)
    dd = ((depth_frame - dmin) * s).astype(np.uint8)
    dst = cv2.applyColorMap(dd,2)

    # Render
    cv2.imshow("Depth",dst)
    cv2.imshow("RGB", color_frame)

    # Wait some seconds and make space for keyboard inputs
    k = cv2.waitKey(1)
    if k == ord("c") or k == 63277:
        if toggle:
            print "Stopping recorder"
        else:
            print "Starting recorder"
        toggle = not toggle
    # Dump
    if toggle and idx % DUMP_INTERVAL == 0:
        q.put((color_frame, depth_frame))
    # This call is mandatory and required by libfreenect2!
    frameListener.release()
    idx += 1

kinect.stop()

# The kinect is has stopped but program needs to finish dumping the data to disk first

p.join()
# kinect.close()

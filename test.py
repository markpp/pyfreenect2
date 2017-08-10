#!/usr/bin/env python
import signal
import time
import os
import datetime

import cv2
import scipy.misc
import numpy as np

import pyfreenect2

import matplotlib.pyplot as plt

REPO_HOME = "/Users/markpp/Documents/github/pyfreenect2/output"

# This is pretty much a straight port of the Protonect program bundled with
# libfreenect2.

# Initialize device
serialNumber = pyfreenect2.getDefaultDeviceSerialNumber()
kinect = pyfreenect2.Freenect2Device(serialNumber, pyfreenect2.USE_CUDA_PACKET_PIPELINE)

# Set up frame listener
frameListener = pyfreenect2.SyncMultiFrameListener(pyfreenect2.Frame.COLOR, pyfreenect2.Frame.IR, pyfreenect2.Frame.DEPTH)

print frameListener
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

# Main loop
idx  = 0
while 1:
    frames = frameListener.waitForNewFrame()

    # Grab a framepair for registration
    rgbFrame = frames.getFrame(pyfreenect2.Frame.COLOR)
    depthFrame = frames.getFrame(pyfreenect2.Frame.DEPTH)

    (undistorted,registered, bigdepth) = registration.apply(rgbFrame=rgbFrame, depthFrame=depthFrame)

    depth_frame = bigdepth.getDepthData()
    h = 480
    w = 640
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
    dmax = 2000.0   # 3m
    s = 255.0/(dmax - dmin)
    dd = ((depth_frame - dmin) * s).astype(np.uint8)
    dst = cv2.applyColorMap(dd,2)

    cv2.imshow("Depth",dst)
    cv2.imshow("RGB", color_frame)

    # Wait some seconds
    k = cv2.waitKey(5)
    if k == ord("c"):
        # Dump both bgr and depth
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S')
        st = "kinectv2_" + st
        print "Saving to " + REPO_HOME + " with prefix " + st
        np.save(REPO_HOME + "/" + st + "_depth.npy", depth_frame)
        np.save(REPO_HOME + "/" + st + "_bgr.npy", color_frame)
    # This call is mandatory and required by libfreenect2!
    frameListener.release()
    if k == ord("q"):
    	break


kinect.stop()
# kinect.close()

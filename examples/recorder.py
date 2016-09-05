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
import argparse

parser = argparse.ArgumentParser(description='Record depth data live and dump to disk.')
parser.add_argument('--s', metavar='subfolder', nargs='+',
                   help='The subfolder to dump data to')

args = parser.parse_args()

sub = ""
if args.s:
    sub = args.s[0]

"""
Config section
"""
# Render RGB in a separate window
render_rgb = False
# JET color scheme
jet = True
# Rescale for visualization
rescale = True
# Folder where to store data
REPO_HOME = "/Users/sebastian/Projects/food3d/data/"
# Dump interval in frames. At 640x480 the loop currently runs at ~11 FPS on a Mac Pro 13'
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

        # Save in compressed format so save some memory
        np.savez_compressed(REPO_HOME + "/" + st + "_depth.npz", depth_frame)
        np.savez_compressed(REPO_HOME + "/" + st + "_bgr.npz", color_frame)


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

# Movie target dir
REPO_HOME += "/" + sub

# Start recording
kinect.start()

# Print useful info
print "Kinect serial: %s" % kinect.serial_number
print "Kinect firmware: %s" % kinect.firmware_version

registration = pyfreenect2.Registration(kinect)

# Initialize OpenCV stuff
if render_rgb:
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
current = time.time()
last = time.time()
fps = 0
fps_idx = 0
while 1:
    fps += 1
    current = time.time()
    if (current - last) > 1:
        last = time.time()
        fps_idx += 1
        if fps_idx % 5 == 0:
            print "[INFO] Running at %i FPS" % fps
        fps = 0

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
    if rescale:
        dmin = 0.0
        dmax = 500.0   # 3m
        s = 255.0/(dmax - dmin)
        dd = ((depth_frame - dmin) * s).astype(np.uint8)
    else:
        dd = depth_frame
    # Apply color scheme
    if jet:
        dst = cv2.applyColorMap(dd,2)
    else:
        dst = dd
    # Render
    # TODO Switch to something with more performance here. Either GLUT or something else
    cv2.imshow("Depth",dst)
    if render_rgb:
        cv2.imshow("RGB", color_frame)

    # Wait some seconds and make space for keyboard inputs
    k = cv2.waitKey(1)
    if k == ord("c") or k == 63277:
        if toggle:
            print "[INFO] Stopping recorder"
        else:
            print "[INFO] Starting recorder with base dir: %s" % REPO_HOME
            # Create directory if necessary
            if not os.path.exists(REPO_HOME):
                os.makedirs(REPO_HOME)
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

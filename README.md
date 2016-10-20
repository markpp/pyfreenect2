pyfreenect2
===========

Python bindings to [libfreenect2](https://github.com/OpenKinect/libfreenect2).

Requirements
---------

- Python2 (python3 support : https://github.com/LovelyHorse/py3freenect2)
- Numpy
- Scipy (as appropriated by python version) :
- Python Imaging Library (used for scipy.misc.im* functions) : http://www.pythonware.com/products/pil/
- OpenCV

Installation
---------

To install, run `sudo python setup.py install`.

Usage
---------

For usage, see `test.py`.

General approach:

1. Grab frames in a loop calling `frames = frameListener.waitForNewFrame()`.
2. Read individual frames like `rgbFrame = frames.getFrame(pyfreenect2.Frame.COLOR)`.
3. Obtain raw data e.g. `color_frame = rgbFrame.getBGRData()`.
4. Do something with it - for example render it using OpenCV.
5. *Important* Release the frames via `frameListener.release()` at the end of the loop.


TODO List
---------
 * Test everything

You can probably find more TODOs in [Issues](https://github.com/tikiking1/pyfreenect2/issues) or by `grep -R TODO .`.

What this fork has in addition (might be outdated at the time of read)
---------
- Registration
- Pipeline argument
- The original code didn't compile on my machine when calling `import_array()`. I fixed the makro in the C++ code.

What to do when working with 3D Food data on a Mac
---------
1. We've only tested this running on system (brew's Cellar) Python, not in any virtual environment.
2. Make sure [libfreenect2](https://github.com/OpenKinect/libfreenect2) is installed properly. They've got a section on how to install on Mac OS X.
3. Once completed, make sure OpenCV and its Python bindings are installed. Instruction can be found online or brew can be used.
4. Run ```recorder.py``` in the examples folder of this repository. Make sure the configuration items within that file (folders) are set to valid and existing locations on disk.
5. Use the commandline argument ```--s``` to specify a sub-folder to dump the data in.
6. Use the c-Key to start capturing. Use the c-Key again to stop capturing. You should see RGB-D pairs being saved in the location specified in the configuration items.
7. Sometimes the program crashes due to LIB_USB exceptions, I unfortunately don't have a workaround for that other than restarting the process.
8. Before quitting make sure to leave the program open for a couple of seconds due to output buffers being emptied by the storage thread.

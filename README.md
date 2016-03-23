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

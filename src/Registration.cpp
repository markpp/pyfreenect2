#include "../pyfreenect2.hpp"
#include <iostream>

using libfreenect2::Freenect2Device;
using libfreenect2::Registration;
using libfreenect2::Frame;

// These are our two containers which are used to write undistorted and registered frames to
Frame *undistorted, *registered, *bigdepth;

PyObject *py_Registration_new(PyObject *self, PyObject *args) {
    PyObject *deviceCapsule = NULL;
    if(!PyArg_ParseTuple(args, "O", &deviceCapsule)) {
        return NULL;
    }
    Freenect2Device *device = (Freenect2Device*) PyCapsule_GetPointer(deviceCapsule, "Freenect2Device");
    Registration *registration = new Registration(device->getIrCameraParams(), device->getColorCameraParams());
    // We create two permanent frame objects where the apply call is writing to
    undistorted = new Frame(512, 424, 4);
    registered = new Frame(512, 424, 4);
    bigdepth = new Frame(1920, 1082, 4);
    // Return the python capsule
    return PyCapsule_New(registration, "Registration", py_Registration_destroy);
}
// Deleting the registration object cleans up the rest of the mem on the heap we allocated here
void py_Registration_destroy(PyObject *registrationCapsule) {
	delete (Registration*) PyCapsule_GetPointer(registrationCapsule, "Registration");
    delete undistorted;
    delete registered;
    delete bigdepth;
}

PyObject *py_Registration_apply(PyObject *self, PyObject *args) {
	PyObject *registrationCapsule = NULL;
    PyObject *rgbFrameCapsule = NULL;
    PyObject *depthFrameCapsule = NULL;
	if(!PyArg_ParseTuple(args, "OOO", &registrationCapsule, &rgbFrameCapsule, &depthFrameCapsule))
		return NULL;
	Registration *registration = (Registration*) PyCapsule_GetPointer(registrationCapsule, "Registration");
    Frame* rgbFrame = (Frame*) PyCapsule_GetPointer(rgbFrameCapsule, "Frame");
    Frame* depthFrame = (Frame*) PyCapsule_GetPointer(depthFrameCapsule, "Frame");

    registration->apply(rgbFrame, depthFrame, undistorted, registered, true, bigdepth);

    PyObject* _undist = PyCapsule_New(undistorted,"Frame", NULL);
    PyObject* _reg = PyCapsule_New(registered,"Frame", NULL);
    PyObject* _bd = PyCapsule_New(bigdepth,"Frame", NULL);
    PyObject *rslt = PyTuple_New(3);
    PyTuple_SetItem(rslt, 0, _undist);
    PyTuple_SetItem(rslt, 1, _reg);
    PyTuple_SetItem(rslt, 2, _bd);
    return rslt;
}

#include "../pyfreenect2.hpp"
#include <iostream>

using libfreenect2::FrameMap;
using libfreenect2::SyncMultiFrameListener;

/**
 * Using a global framemap here in order to be able to delete it as well
 * TODO Kinda ugly
 */
FrameMap fm;
FrameMap& getGlobalFrameMap() { return fm; }

void py_SyncMultiFrameListener_destroy(PyObject *listenerCapsule) {
	delete ((SyncMultiFrameListener*) PyCapsule_GetPointer(listenerCapsule,
							       "SyncMultiFrameListener"));
}

PyObject *py_SyncMultiFrameListener_new(PyObject *self, PyObject *args) {
	unsigned int frame_types = 0;
	if(!PyArg_ParseTuple(args, "I", &frame_types))
		return NULL;
	SyncMultiFrameListener *listener = new SyncMultiFrameListener(frame_types);
	std::cout << "listener in ext: " << listener << std::endl;
	return PyCapsule_New(listener,
			     "SyncMultiFrameListener",
			     py_SyncMultiFrameListener_destroy);
}

PyObject *py_SyncMultiFrameListener_waitForNewFrame(PyObject *self, PyObject *args) {
	PyObject *listenerCapsule = NULL;
	if(!PyArg_ParseTuple(args, "O", &listenerCapsule))
		return NULL;
	SyncMultiFrameListener *listener = (SyncMultiFrameListener*) PyCapsule_GetPointer(listenerCapsule, "SyncMultiFrameListener");
	// FrameMap *frames = new FrameMap;
	listener->waitForNewFrame(fm);
	return PyCapsule_New(&fm, "FrameMap", py_FrameMap_destroy);
}

PyObject *py_SyncMultiFrameListener_release(PyObject *self, PyObject *args) {
    PyObject *listenerCapsule = NULL;
	if(!PyArg_ParseTuple(args, "O", &listenerCapsule))
		return NULL;
	SyncMultiFrameListener *listener = (SyncMultiFrameListener*) PyCapsule_GetPointer(listenerCapsule, "SyncMultiFrameListener");
	listener->release(fm);
    Py_INCREF(Py_None);
	return Py_None;

}

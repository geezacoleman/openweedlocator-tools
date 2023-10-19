# NOTE this code has been adapted from the PyImageSearch video classes.
# Please reference the original repository (https://github.com/PyImageSearch/imutils/blob/master/imutils/video)

from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread, Event
import cv2

class PiCameraStream:
    def __init__(self, resolution=(320, 240), framerate=32, **kwargs):
        self.camera = PiCamera()

        self.camera.resolution = resolution
        self.camera.framerate = framerate

        # set optional camera parameters (refer to PiCamera docs)
        for (arg, value) in kwargs.items():
            setattr(self.camera, arg, value)

        # initialize the stream
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)

        self.frame = None
        self.stopped = Event()

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        for f in self.stream:
            self.frame = f.array
            self.rawCapture.truncate(0)

            if self.stopped.is_set():
                self.release_resources()
                return

    def read(self):
        return self.frame

    def stop(self):
        self.stopped.set()

    def release_resources(self):
        self.stream.close()
        self.rawCapture.close()
        self.camera.close()

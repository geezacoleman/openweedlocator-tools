from picamera2 import Picamera2
from libcamera import Transform
import time
from threading import Thread, Event

class PiCamera2Stream:

    def __init__(self, resolution=(320, 248), framerate=32, **kwargs):
        self.size = resolution # picamera2 use size instead of resolution, keeping this consistent
        self.framerate = framerate

        self.config = {
            "format": 'XRGB8888',
            "size": self.size
        }
        # Update config with any additional/overridden parameters
        self.config.update(kwargs)

        # Initialize the camera and stream
        self.picam2 = Picamera2()
        self.picam2.set_logging(Picamera2.INFO)
        self.picam2.configure(self.picam2.create_preview_configuration( main=self.config))

        self.picam2.start()
        time.sleep(2)  # Allow the camera time to warm up

        self.frame = None
        self.stopped = Event()

    def start(self):
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def update(self):
        while not self.stopped.is_set():
            frame = self.picam2.capture_array("main")
            self.frame = frame
            time.sleep(0.001)  # Slow down loop a little

    def read(self):
        return self.frame

    def stop(self):
        self.stopped.set()
        self.thread.join()
        self.picam2.stop()  # stop picamera2 libcamera
        time.sleep(2)  # allow the camera time to be released

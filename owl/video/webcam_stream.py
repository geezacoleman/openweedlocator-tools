# NOTE this code has been adapted from the PyImageSearch video classes.
# Please reference the original repository (https://github.com/PyImageSearch/imutils/blob/master/imutils/video)

from threading import Thread, Event
import cv2


class WebcamStream:
    def __init__(self, src=0, name="WebcamVideoStream"):
        self.stream = cv2.VideoCapture(src)

        # Check if the stream opened successfully
        if not self.stream.isOpened():
            raise ValueError("Unable to open video source:", src)

        # read the first frame from the stream
        self.grabbed, self.frame = self.stream.read()

        # initialize the thread name and the stop event
        self.name = name
        self.stop_event = Event()

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name)
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while not self.stop_event.is_set():
            # Read the next frame from the stream
            self.grabbed, self.frame = self.stream.read()

            # If not grabbed, end of the stream has been reached.
            if not self.grabbed:
                break

        # Clean up resources after loop is done
        self.stream.release()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # signal the thread to stop and wait for it
        self.stop_event.set()

# NOTE this code has been adapted from the PyImageSearch FileVideoStream class.
# Please reference the original repository (https://github.com/PyImageSearch/imutils/blob/master/imutils/video/filevideostream.py)
import cv2
import logging
from queue import Queue
from threading import Thread, Event, Condition

logging.basicConfig(level=logging.INFO)


class FileVideoStream:
    def __init__(self, path, queue_size=128):
        self.stream = cv2.VideoCapture(path)
        if not self.stream.isOpened():
            raise ValueError("Unable to open video file: {}".format(path))

        self.stopped = Event()
        self.queue_not_full = Condition()
        self.Q = Queue(maxsize=queue_size)

        self.thread = Thread(target=self.update)
        self.thread.daemon = True

    def start(self):
        self.thread.start()
        return self

    def update(self):
        while not self.stopped.is_set():
            with self.queue_not_full:
                while self.Q.full():
                    self.queue_not_full.wait()

                grabbed, frame = self.stream.read()

                if not grabbed:
                    self.stopped.set()
                else:
                    self.Q.put(frame)

    def read(self):
        frame = self.Q.get()

        with self.queue_not_full:
            self.queue_not_full.notify()

        return frame

    def running(self):
        return not self.Q.empty() or not self.stopped.is_set()

    def stop(self):
        self.stopped.set()
        self.thread.join()

        if self.stream.isOpened():
            self.stream.release()

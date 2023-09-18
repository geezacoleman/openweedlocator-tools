import cv2
import glob
import pathlib

from ..greenongreen import GreenOnGreen
from ..greenonbrown import GreenOnBrown

def _get_weed_detector(algorithm, model_path=None):
    if algorithm == 'gog':
        return GreenOnGreen(model_path=model_path)
    else:
        return GreenOnBrown(algorithm=algorithm)

def webcam(algorithm, model_path=None):
    detector = _get_weed_detector(algorithm=algorithm, model_path=model_path)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[Error] Could not open camera.")
        exit()

    while True:
        ret, frame = cap.read()

        _, boxes, weedCenters, image = detector.predict(frame.copy(), resolution=None)
        cv2.imshow('Video Feed', image)

        # Exit with 'ESC' key
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def video(algorithm):
    detector = _get_weed_detector(algorithm=algorithm, model_path=model_path)
    if input_file_or_directory:
        self.cam = FrameReader(path=input_file_or_directory,
                               resolution=self.resolution,
                               loop_time=self.image_loop_time)
        self.frame_width, self.frame_height = self.cam.resolution

        self.logger.log_line(f'[INFO] Using {self.cam.input_type} from {input_file_or_directory}...', verbose=True)


def images(algorithm):
    detector = _get_weed_detector(algorithm=algorithm, model_path=model_path)
    pass

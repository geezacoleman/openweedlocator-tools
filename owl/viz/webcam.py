import cv2
import glob
import pathlib
from ..utils.io import get_weed_detector, load_config, setup_detector
from ..utils.image import FrameReader

import cv2

def webcam(algorithm='exhsv',
           model_path='models/yolov8n.pt',
           config_file="owl/config/day-sensitivity-1.json", **kwargs):
    weed_detector = get_weed_detector(algorithm=algorithm, model_path=model_path)

    config = load_config(config_file)
    config.update(kwargs)

    reader = cv2.VideoCapture(0)

    if not reader.isOpened():
        print("[Error] Could not open camera.")
        exit()

    while True:
        ret, frame = reader.read()

        _, _, _, image = setup_detector(weed_detector=weed_detector,
                                                  frame=frame.copy(),
                                                  config_file=config_file)
        cv2.imshow('Video Feed', image)

        # Exit with 'ESC' key
        if cv2.waitKey(1) == 27:
            break

    reader.release()
    cv2.destroyAllWindows()

import cv2
import glob
import pathlib
import json

from ..detectors import GreenOnGreen, GreenOnBrown
from .frame_reader import FrameReader

def _get_weed_detector(algorithm, model_path=None, platform='windows'):
    if algorithm == 'gog':
        return GreenOnGreen(model_path=model_path, platform=platform)
    else:
        return GreenOnBrown(algorithm=algorithm)

def _load_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

def _inference(weed_detector, frame, config_file="owl/config/day-sensitivity-1.json"):
    config = _load_config(config_file=config_file)

    # load general parameters
    show_display = config.get('show_display')  # Assuming this is also coming from the config
    algorithm = config.get('algorithm')
    resolution = tuple(config.get('resolution'))

    # load GreenonBrown parameters
    exgMin = config.get('exgMin')
    exgMax = config.get('exgMax')
    hueMin = config.get('hueMin')
    hueMax = config.get('hueMax')
    saturationMin = config.get('saturationMin')
    saturationMax = config.get('saturationMax')
    brightnessMin = config.get('brightnessMin')
    brightnessMax = config.get('brightnessMax')
    minArea = config.get('minArea')
    invert_hue = config.get('invert_hue')

    # load GreenonGreen parameters
    conf = config.get('confidence')
    iou = config.get('iou')
    filter_id = config.get('filter_id')

    if algorithm == 'gog':
        return weed_detector.inference(
            frame.copy(),
            conf=conf,
            iou=iou,
            resolution=resolution)

    else:
        return weed_detector.inference(
            frame.copy(),
            exgMin=exgMin,
            exgMax=exgMax,
            hueMin=hueMin,
            hueMax=hueMax,
            saturationMin=saturationMin,
            saturationMax=saturationMax,
            brightnessMin=brightnessMin,
            brightnessMax=brightnessMax,
            show_display=show_display,
            algorithm=algorithm,
            minArea=minArea,
            invert_hue=invert_hue
        )


def webcam(algorithm='exhsv', model_path=None, config_file="owl/config/day-sensitivity-1.json", **kwargs):
    weed_detector = _get_weed_detector(algorithm=algorithm, model_path=model_path)

    config = _load_config(config_file)
    config.update(kwargs)

    reader = cv2.VideoCapture(0)

    if not reader.isOpened():
        print("[Error] Could not open camera.")
        exit()

    while True:
        ret, frame = reader.read()

        _, _, _, image = _inference(weed_detector=weed_detector,
                                                  frame=frame.copy(),
                                                  config_file=config_file)
        cv2.imshow('Video Feed', image)

        # Exit with 'ESC' key
        if cv2.waitKey(1) == 27:
            break

    reader.release()
    cv2.destroyAllWindows()


def images_and_video(media_path='videos/test_video1.mp4', algorithm='exhsv', model_path=None,
                     config_file="owl/config/day-sensitivity-1.json", **kwargs):
    weed_detector = _get_weed_detector(algorithm=algorithm, model_path=model_path)

    config = _load_config(config_file)
    config.update(kwargs)
    resolution = config.get('resolution')

    reader = FrameReader(path=media_path,
                         resolution=resolution)

    while True:
        ret, frame = reader.read()

        _, _, _, image = _inference(weed_detector=weed_detector,
                                    frame=frame.copy(),
                                    config_file=config_file)
        cv2.imshow('Video Feed', image)

        # Exit with 'ESC' key
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    webcam()
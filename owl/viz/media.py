from owl.utils.image import FrameReader
from owl.utils.io import get_weed_detector, load_config, setup_and_run_detector

import cv2

def webcam(
        src=0,
        algorithm="exhsv",
        model_path="owl/models/yolov8n.pt",
        config_file="owl/config/day-sensitivity-1.json", **kwargs):
    weed_detector = get_weed_detector(algorithm=algorithm, model_path=model_path)

    config = load_config(config_file)
    config.update(kwargs)
    config.update({"algorithm": f"{algorithm}"})

    reader = cv2.VideoCapture(src)

    if not reader.isOpened():
        print("[ERROR] Could not open camera.")
        exit()

    while True:
        ret, frame = reader.read()

        _, _, _, image = setup_and_run_detector(weed_detector=weed_detector,
                                                frame=frame.copy(),
                                                config=config)
        cv2.imshow('Video Feed', image)

        # exit with 'ESC'
        if cv2.waitKey(1) == 27:
            break

    reader.release()
    cv2.destroyAllWindows()


def images_and_video(media_path='media',
                     algorithm='exhsv',
                     model_path='models/yolov8n.pt',
                     config_file="owl/config/day-sensitivity-1.json", **kwargs):

    weed_detector = get_weed_detector(algorithm=algorithm, model_path=model_path)

    config = load_config(config_file)
    config.update(kwargs)
    config.update({"algorithm": f"{algorithm}"})
    resolution = config.get('resolution')

    reader = FrameReader(path=media_path,
                         resolution=resolution)

    while True:
        frame = reader.read()

        _, _, _, image = setup_and_run_detector(weed_detector=weed_detector,
                                    frame=frame.copy(),
                                    config=config)
        cv2.imshow('Detection', image)

        # exit with 'ESC'
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()
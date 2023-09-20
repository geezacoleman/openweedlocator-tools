from ..utils.io import get_weed_detector, load_config, setup_and_run_detector
from ..utils.image import FrameReader

import cv2

def images_and_video(media_path='media/test_video1.mp4',
                     algorithm='exhsv',
                     model_path='models/yolov8n.pt',
                     config_file="owl/config/day-sensitivity-1.json", **kwargs):

    weed_detector = get_weed_detector(algorithm=algorithm, model_path=model_path)

    config = load_config(config_file)
    config.update(kwargs)
    resolution = config.get('resolution')

    reader = FrameReader(path=media_path,
                         resolution=resolution)

    while True:
        ret, frame = reader.read()

        _, _, _, image = setup_and_run_detector(weed_detector=weed_detector,
                                    frame=frame.copy(),
                                    config_file=config_file)
        cv2.imshow('Detection', image)

        # Exit with 'ESC' key
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()
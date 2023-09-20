import json

from ..detectors import GreenOnGreen, GreenOnBrown

def get_weed_detector(algorithm, model_path=None, platform='windows'):
    if algorithm == 'gog':
        return GreenOnGreen(model_path=model_path, platform=platform)
    else:
        return GreenOnBrown(algorithm=algorithm)

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

def setup_and_run_detector(weed_detector, frame, config_file="owl/config/day-sensitivity-1.json"):
    config = load_config(config_file=config_file)

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


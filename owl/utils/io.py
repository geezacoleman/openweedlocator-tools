from owl.utils import config as CONFIG_FILES
import warnings
def get_weed_detector(algorithm, model_path=None, platform='desktop'):
    from owl.detection import GreenOnGreen, GreenOnBrown
    if algorithm == 'gog':
        return GreenOnGreen(model_path=model_path, platform=platform)

    else:
        return GreenOnBrown()

def load_config(CONFIG_NAME):
    try:
        config = getattr(CONFIG_FILES, CONFIG_NAME)
    except AttributeError:
        warnings.warn("Invalid configuration name, defaulting to CONFIG_DAY_SENSITIVITY_1")
        config = CONFIG_FILES.CONFIG_DAY_SENSITIVITY_1

    return config

def setup_and_run_detector(weed_detector, frame, config):
    # load general parameters
    show_display = config.get('show_display')
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
    conf = config.get('conf')
    iou = config.get('iou')
    filter_id = None if config.get('filter_id') == "null" or config.get('filter_id') == "" else config.get('filter_id')

    if algorithm == 'gog':
        return weed_detector.find(
            frame.copy(),
            conf=conf,
            iou=iou,
            resolution=resolution,
            filter_id=filter_id
        )

    else:
        return weed_detector.find(
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



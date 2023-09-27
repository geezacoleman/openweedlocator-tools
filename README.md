# Official OpenWeedLocator Toolkit
Simplifying the integration of weed detection into your platform.

[![OWL-tools](https://github.com/geezacoleman/openweedlocator-tools/actions/workflows/owl-testing.yml/badge.svg)](https://github.com/geezacoleman/openweedlocator-tools/actions/workflows/owl-testing.yml)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://owl-tools.streamlit.app/)

## Overview
The OpenWeedLocator (OWL) is an open-source weed detection device for low-cost, 
DIY site-specific weed management. The full project can be found [here](https://github.com/geezacoleman/OpenWeedLocator). 
Here, we're making the software that supports the OWL more accesible with an easy-to-use API, 
so you can integrate weed detection into your own devices and services more easily 
by simply calling `GreenonBrown.find()`.

Currently, owl-tools supports green-on-brown detection on all platforms, and green-on-green
on desktops through the Ultralytics package. Train your only YOLO algorithms and simply integrate 
them by providing a path to the trained `model.pt`.

In the future, we will support plant counting, GPS integration and green-on-green 
on edge devices (Jetson Nano, Raspberry Pi). If you're nterested in specific features,
feel free to raise an issue or pull request.

## Installation
To install the latest version of `openweedlocator-tools` simply run:
### Desktop (GreenOnGreen + GreenOnBrown)
```
pip install openweedlocator-tools[desktop]
```
### Raspberry Pi (GreenOnBrown only)
```
pip install openweedlocator-tools[rpi]
```

## Quick Start
```Python
from owl.viz import webcam, images_and_video

# Run using your webcam
webcam(algorithm='gog', model_path='models/yolov8n.pt) # press escape to exit, add your own model path as required or clone this repository

# or 
images_and_video(media_path='path/to/your/media_files)
```

## Streamlit App
Try it for yourself now with the official Streamlit app!
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://owl-tools.streamlit.app/)

## Example Usage
These examples shows the basic functionality of the detection classes, GreenOnBrown and GreenOnGreen to operate on a video.

```Python
from owl.detection import GreenOnBrown
import cv2

VIDEO_PATH = r'media/test_video_1.avi'
ALGORITHM = 'exhsv'

weed_detector = GreenOnBrown()

video_feed = cv2.VideoCapture(VIDEO_PATH)

while True:
    ret, frame = video_feed.read()

    if not ret:
        break

    # the weed_detector.find() method returns a tuple with four items
    results = weed_detector.find(frame.copy(),
                                 exgMin=30,
                                 exgMax=250,
                                 hueMin=30,
                                 hueMax=90,
                                 brightnessMin=5,
                                 brightnessMax=200,
                                 saturationMin=30,
                                 saturationMax=255,
                                 minArea=1,
                                 show_display=False,
                                 algorithm=ALGORITHM,
                                 invert_hue=False)

    contours, bounding_boxes, weed_centres, display_image = results
    cv2.imshow('OWL-tput', display_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

Instead of instantiating your own `GreenOnBrown()` instance, you can make the most of 
`owl.utils.io.get_weed_detector()` and `owl.utils.io.setup_and_run_detector()` functions. The `setup_and_run_detector()` function
makes it easy to use the inbuilt `owl.utils.config.CONFIG_DAY_SENSITIVITY_1`, to avoid providing all
variables yourself. For example:

```Python
from owl.utils.io import get_weed_detector, load_config, setup_and_run_detector
import cv2

CONFIG_NAME = "CONFIG_DAY_SENSITIVITY_1"
ALGORITHM = 'exhsv'
MODEL_PATH = None
VIDEO_PATH = r'media/test_video_1.avi'
PLATFORM = 'desktop'

weed_detector = get_weed_detector(algorithm=ALGORITHM, model_path=MODEL_PATH, platform='desktop')

config = load_config(CONFIG_NAME)
config.update({"algorithm": f"{ALGORITHM}"})

video_feed = cv2.VideoCapture(VIDEO_PATH)

while True:
    ret, frame = video_feed.read()

    if not ret:
        break

    _, _, _, display_image = setup_and_run_detector(weed_detector=weed_detector,
                                            frame=frame.copy(),
                                            config=config)

    cv2.imshow('OWL-tput', display_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
```

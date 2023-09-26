# Official OpenWeedLocator Toolkit
Simplifying the integration of weed detection into your platform.

[![OWL-tools](https://github.com/geezacoleman/openweedlocator-tools/actions/workflows/owl-testing.yml/badge.svg)](https://github.com/geezacoleman/openweedlocator-tools/actions/workflows/owl-testing.yml)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://owl-tools.streamlit.app/)

## Overview
The OpenWeedLocator (OWL) is an open-source weed detection device for low-cost, 
DIY site-specific weed management. Here, we're making the software that supports 
the OWL more accesible with an easy-to-use API, so you can integrate weed detection 
into your own devices and services more easily by simply calling 
`GreenonBrown.find()`.

Currently, it supports green-on-brown detection on all platforms, and green-on-green
on desktops through the Ultralytics package.

In the future, we will support plant counting, GPS integration and green-on-green 
on edge devices (Jetson Nano, Raspberry Pi)

## Installation
To install the latest version of `openweedlocator-tools` simply run:
### Desktop (GreenOnGreen + GreenOnBrown)
```
pip install openweedlocator-tools[desktop]
```
### Raspberry Pi (
```
pip install openweedlocator-tools[rpi]
```

Note, owl-tools will 
## Quick Start
```Python
from owl.viz import webcam, images_and_video

# Run using your webcam
webcam(algorithm='gog', model_path='models/yolov8n.pt) # press escape to exit, add your own model path as required or clone this repository

# or 
images_and_video(media_path='path/to/your/media_files
```

## Example
This example shows the basic functionality of the detection classes, GreenOnBrown and GreenOnGreen to operate on a video.
```Python
from owl.detection import GreenOnBrown
import cv2

video_path = 'path_to_video.mp4'

weed_detector = GreenOnBrown()

video_feed = cv2.VideoCapture(video_path)

while True:
    ret, frame = video_feed.read()

    if not ret:
        break

    # the weed_detector.find() method returns a tuple with four items
    results = weed_detector.find(image,
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
                                 algorithm='exg',
                                 invert_hue=False)
    
    contours, bounding_boxes, weed_centres, display_image = results
    cv2.imshow('OWL-tput', display_image)
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

```
Instead of instantiating your own `GreenOnBrown()` instance, you can make the most of the 
`get_weed_detector()` and `setup_and_run_detector()`. The `setup_and_run_detector()` function 
makes it easy to use the inbuilt `config.CONFIG_DAY_SENSITIVITY_1`, to avoid providing all
variables yourself. For example:

```Python
weed_detector = get_weed_detector(algorithm=algorithm, model_path=model_path, platform=platform)

algorithm = 'exhsv'
CONFIG_NAME="CONFIG_DAY_SENSITIVITY_1"
config = load_config(CONFIG_NAME)
config.update({"algorithm": f"{algorithm}"})

video_feed = cv2.VideoCapture(video_path)

while True:
    ret, frame = video_feed.read()

    _, _, _, image = setup_and_run_detector(weed_detector=weed_detector,
                                            frame=frame.copy(),
                                            config=config)
    cv2.imshow('Video Feed', image)

    cv2.imshow('OWL-tput', display_image)
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
```


## Streamlit App
Try it for yourself now with the online, Streamlit app!
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://owl-tools.streamlit.app/)

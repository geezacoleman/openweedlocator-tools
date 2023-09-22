# Official OpenWeedLocator Toolkit
Simplifying the integration of weed detection into your platform.

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
### Desktop
```
pip install openweedlocator-tools[desktop]
```
### Raspberry Pi
```
pip install openweedlocator-tools[rpi]
```

## Quick Start
```
from owl.viz import webcam, images_and_video
# Run using your webcam
webcam(algorithm='gog')

```

## Examples
### 
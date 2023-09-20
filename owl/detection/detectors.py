from owl.utils.algorithms import  *
from imutils import grab_contours

from pathlib import Path
import numpy as np
import sys
import cv2


class GreenOnBrown:
    def __init__(self, algorithm='exg', labels='weed'):
        self.algorithm = algorithm
        self.label = labels

    def find(self,
                  image,
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
                  invert_hue=False):
        '''
        Uses a provided algorithm and contour detection to determine green objects in the image. Min and Max
        thresholds are provided.
        :param image: input image to be analysed
        :param exgMin: minimum exG threshold value
        :param exgMax: maximum exG threshold value
        :param hueMin: minimum hue threshold value
        :param hueMax: maximum hue threshold value
        :param brightnessMin: minimum brightness threshold value
        :param brightnessMax: maximum brightness threshold value
        :param saturationMin: minimum saturation threshold value
        :param saturationMax: maximum saturation threshold value
        :param minArea: minimum area for the detection - used to filter out small detections
        :param show_display: True: show windows; False: operates in headless mode
        :param algorithm: the algorithm to use. Defaults to ExG if not correct
        :return: returns the contours, bounding boxes, centroids and the image on which the boxes have been drawn
        '''
        self.weedCenters = []
        self.boxes = []

        # different algorithm options, add in your algorithm here if you make a new one!
        threshedAlready = False
        if algorithm == 'exg':
            output = exg(image)

        elif algorithm == 'exgr':
            output = exgr(image)

        elif algorithm == 'maxg':
            output = maxg(image)

        elif algorithm == 'nexg':
            output = exg_standardised(image)

        elif algorithm == 'exhsv':
            output = exg_standardised_hue(image, hueMin=hueMin, hueMax=hueMax,
                                          brightnessMin=brightnessMin, brightnessMax=brightnessMax,
                                          saturationMin=saturationMin, saturationMax=saturationMax,
                                          invert_hue=invert_hue)

        elif algorithm == 'hsv':
            output, threshedAlready = hsv(image, hueMin=hueMin, hueMax=hueMax,
                                          brightnessMin=brightnessMin, brightnessMax=brightnessMax,
                                          saturationMin=saturationMin, saturationMax=saturationMax,
                                          invert_hue=invert_hue)

        elif algorithm == 'gndvi':
            output = gndvi(image)

        else:
            output = exg(image)
            print(f'[WARNING] Selected algorithm {self.algorithm} unavailable. Defaulting to ExG')

        # run the thresholds provided
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

        # if not a binary image, run an adaptive threshold on the area that fits within the thresholded bounds.
        if not threshedAlready:
            output = np.where(output > exgMin, output, 0)
            output = np.where(output > exgMax, 0, output)
            output = np.uint8(np.abs(output))
            if show_display:
                cv2.imshow("HSV Threshold on ExG", output)

            thresholdOut = cv2.adaptiveThreshold(output, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 2)
            thresholdOut = cv2.morphologyEx(thresholdOut, cv2.MORPH_CLOSE, kernel, iterations=1)

        # if already binary, run morphological operations to remove any noise
        if threshedAlready:
            thresholdOut = cv2.morphologyEx(output, cv2.MORPH_CLOSE, kernel, iterations=5)

        if show_display:
            cv2.imshow("Binary Threshold", thresholdOut)

        # find all the contours on the binary images
        self.cnts = cv2.findContours(thresholdOut.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.cnts = grab_contours(self.cnts)

        # loop over all the detected contours and calculate the centres and bounding boxes
        for c in self.cnts:
            # filter based on total area of contour
            if cv2.contourArea(c) > minArea:
                # calculate the min bounding box
                startX, startY, boxW, boxH = cv2.boundingRect(c)
                endX = startX + boxW
                endY = startY + boxH

                cv2.putText(image, self.label, (startX, startY + 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
                cv2.rectangle(image, (int(startX), int(startY)), (endX, endY), (0, 0, 255), 2)

                # save the bounding box
                self.boxes.append([startX, startY, boxW, boxH])
                # compute box center
                centerX = int(startX + (boxW / 2))
                centerY = int(startY + (boxH / 2))
                self.weedCenters.append([centerX, centerY])

        # returns the contours, bounding boxes, centroids and the image on which the boxes have been drawn
        return self.cnts, self.boxes, self.weedCenters, image


class GreenOnGreen:
    def __init__(self, model_path='owl/models/yolov8n.pt', platform='windows'):
        self.model_path = Path(model_path)
        self.results = None
        self.weedCenters = []
        self.boxes = []

        if platform == 'windows':
            from ultralytics import YOLO
            import torch
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        else:
            print(f'[INFO] GreenonGreen not yet implemented on {platform} platform')
            sys.exit()

        if not self._validate_model_path(self.model_path):
            raise ValueError(f"[ERROR] Invalid model path provided {str(self.model_path)}.")

        print(f'[INFO] Loading model {str(self.model_path.stem)}...')
        self.model = YOLO(self.model_path)

    def find(self, image, conf=0.4, iou=0.7, resolution=(640, 420), filter_id=None):
        image, resolution = self._validate_resolution(image, resolution=resolution)
        self.results = self.model(image, conf=conf, iou=iou,
                                  imgsz=(resolution[1], resolution[0]),
                                  save=False, stream=True, classes=filter_id, verbose=False)

        for result in self.results:
            boxes = result.boxes.to(self.device).numpy()
            for box in boxes:
                startX = round(box.xyxyn[0][0]*resolution[0])
                startY = round(box.xyxyn[0][1]*resolution[1])

                endX = round(box.xyxyn[0][2]*resolution[0])
                endY = round(box.xyxyn[0][3]*resolution[1])

                boxW = round(box.xywhn[0][2]*resolution[0])
                boxH = round(box.xywhn[0][3]*resolution[1])
                self.boxes.append([startX, startY, boxW, boxH])

                centerX = round(startX + ((endX - startX) / 2))
                centerY = round(startY + ((endY - startY) / 2))
                self.weedCenters.append([centerX, centerY])

                percent = int(100 * box.conf[0])
                label = f'{percent}% {result.names[int(box.cls[0])]}'

                cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)

                cv2.circle(image, center=(centerX, centerY), radius=5, thickness=-1, color=(255, 0, 0))
                cv2.putText(image, label, (startX, startY + 30), cv2.FONT_HERSHEY_SIMPLEX, .75, (255, 0, 0), 2)

        return None, self.boxes, self.weedCenters, image

    @staticmethod
    def _validate_resolution(image, resolution):
        inputH = image.shape[0]
        inputW = image.shape[1]

        if resolution is None:
            modelH = inputH
            modelW = inputW
        else:
            modelH = resolution[1]
            modelW = resolution[0]

        if inputW != modelW or inputH != modelH:
            image = cv2.resize(image, (modelW, modelH))

        return image, (modelW, modelH)

    @staticmethod
    def _validate_model_path(model_path) -> bool:
        if not model_path.exists():
            print(f"[ERROR] {model_path} could not be found.")
            return False

        # ensure path is .pt model
        if model_path.suffix != '.pt':
            print(f"[ERROR] {model_path} is not a .pt file.")
            return False

        return True







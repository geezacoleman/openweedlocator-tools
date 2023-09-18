from pathlib import Path
import cv2
import sys

import imutils

class GreenOnGreen:
    def __init__(self, model_path='owl/models/yolov8n.pt', label_file='models/labels.txt', platform='windows'):
        self.model_path = model_path
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
            raise ValueError("[ERROR] Invalid model path provided.")

        print(f'[INFO] Loading model...')
        self.model = YOLO(self.model_path)

    def predict(self, image, conf=0.4, iou=0.7, resolution=(640, 420)):
        image, resolution = self._validate_resolution(image, resolution=resolution)
        self.results = self.model(image, conf=conf, iou=iou, imgsz=(resolution[1], resolution[0]), save=False, stream=True,)

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
    def _validate_model_path(path: str) -> bool:
        model_path = Path(path)

        if not model_path.exists():
            print(f"[ERROR] {model_path} could not be found.")
            return False

        # ensure path is .pt model
        if model_path.suffix != '.pt':
            print(f"[ERROR] {model_path} is not a .pt file.")
            return False

        return True

def test_webcam():
    detector = GreenOnGreen()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[Error] Could not open camera.")
        exit()

    while True:
        ret, frame = cap.read()

        _, boxes, weedCenters, image = detector.predict(frame.copy(), resolution=None)
        cv2.imshow('Video Feed', image)

        # Exit with 'ESC' key
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test()






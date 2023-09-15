
from pathlib import Path
from glob import glob
import cv2
import os


class GreenOnGreen:
    def __init__(self, algorithm='gog', label_file='models/labels.txt'):
        if algorithm == 'gog':
            self.algorithm_file = Path(glob('models/*.tflite')[0])
            print(f'[INFO] Using {self.algorithm_file.stem} model...')

        elif algorithm.endswith('.tflite'):
            self.algorithm_file = Path(algorithm)
            print(f'[INFO] Using {self.algorithm_file.stem} model...')

        else:
            print(f'[ERROR] Unknown algorithm {algorithm}, using default...')
            self.algorithm_file = Path(glob('models/*.tflite')[0])
            print(f'[INFO] Using {self.algorithm_file.stem} model...')

        self.labels = read_label_file(label_file)
        self.interpreter = make_interpreter(self.algorithm_file.as_posix())
        self.interpreter.allocate_tensors()
        self.inference_size = input_size(self.interpreter)
        self.objects = None

    def inference(self, image, confidence=0.5, filter_id=0):
        cv2_im_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2_im_rgb = cv2.resize(cv2_im_rgb, self.inference_size)
        run_inference(self.interpreter, cv2_im_rgb.tobytes())
        self.objects = get_objects(self.interpreter, confidence)
        self.filter_id = filter_id

        height, width, channels = image.shape
        scale_x, scale_y = width / self.inference_size[0], height / self.inference_size[1]
        self.weedCenters = []
        self.boxes = []

        for det_object in self.objects:
            if det_object.id == self.filter_id:
                bbox = det_object.bbox.scale(scale_x, scale_y)
                startX, startY = int(bbox.xmin), int(bbox.ymin)
                endX, endY = int(bbox.xmax), int(bbox.ymax)
                boxW = endX - startX
                boxH = endY = startY

                # save the bounding box
                self.boxes.append([startX, startY, boxW, boxH])
                # compute box center
                centerX = int(startX + (boxW / 2))
                centerY = int(startY + (boxH / 2))
                self.weedCenters.append([centerX, centerY])

                percent = int(100 * det_object.score)
                label = f'{percent}% {self.labels.get(det_object.id, det_object.id)}'
                cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
                cv2.putText(image, label, (startX, startY + 30),
                                     cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
            else:
                pass
        # print(self.weedCenters)
        return None, self.boxes, self.weedCenters, image








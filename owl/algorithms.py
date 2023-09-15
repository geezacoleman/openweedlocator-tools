import numpy as np
import cv2

### Adding a new algorithm ###
"""
To add a new algorithm the only requirement is that it accepts a BGR (opencv) image and returns a grayscale
image as an output. If it returns a binary image (like hsv) then it must return a boolean True in addition to the image
as it has already been thresholded.
"""
##############################

def exg(image):
    """
    Takes an image and processes it using ExG. Returns a single channel exG output.
    Developed by Woebbecke et al. 1995.
    :return: grayscale image
    """
    # using array slicing to split into channels
    blue = image[:, :, 0].astype(np.float32)
    green = image[:, :, 1].astype(np.float32)
    red = image[:, :, 2].astype(np.float32)
    # cv2.imshow('blue', blue.astype('uint8'))
    # cv2.imshow('green', green.astype('uint8'))
    # cv2.imshow('red', red.astype('uint8'))

    imgOut = 2 * green - red - blue
    imgOut = np.clip(imgOut, 0, 255)
    imgOut = imgOut.astype('uint8')

    # cv2.imshow('ExG', imgOut)
    return imgOut

def maxg(image):
    '''
    Takes an input image in int8 format and calculates the 'maxg' algorithm based on the following publication:
    'Weed Identification Using Deep Learning and Image Processing in Vegetable Plantation', Jin et al. 2021
    :param image: image as a BGR array (i.e. opened with opencv not PIL)
    :return: grayscale image
    '''
    # using array slicing to split into channels with float32 for calculation
    blue = image[:, :, 0].astype(np.float32)
    green = image[:, :, 1].astype(np.float32)
    red = image[:, :, 2].astype(np.float32)

    imgOut = 24 * green - 19 * red - 2 * blue
    imgOut = (imgOut / np.amax(imgOut)) * 255 # scale image between 0 - 255
    imgOut = imgOut.astype('uint8')

    return imgOut

def exg_standardised(image):
    '''
    Takes an input image in int8 format and calculates the standardised ExG algorithm
    :param image: image as a BGR array (i.e. opened with opencv not PIL)
    :return: returns a grayscale image
    '''
    blue = image[:, :, 0].astype(np.float32)
    green = image[:, :, 1].astype(np.float32)
    red = image[:, :, 2].astype(np.float32)
    chanSum = red + green + blue
    chanSum = np.where(chanSum == 0, 1, chanSum)

    b = blue / chanSum
    g = green / chanSum
    r = red / chanSum

    imgOut = 255 * (2 * g - r - b)
    imgOut = np.where(imgOut < 0, 0, imgOut)
    imgOut = np.where(imgOut > 255, 255, imgOut)

    imgOut = imgOut.astype('uint8')
    # cv2.imshow('ExG Standardised', imgOut)

    return imgOut

def exg_standardised_hue(image,
                         hueMin=30,
                         hueMax=90,
                         brightnessMin=10,
                         brightnessMax=220,
                         saturationMin=30,
                         saturationMax=255,
                         invert_hue=False):
    '''
    Takes an image and performs a combined ExG + HSV algorithm
    :param image: image as a BGR array (i.e. opened with opencv not PIL)
    :param hueMin: minimum hue value
    :param hueMax: maximum hue value
    :param brightnessMin: minimum 'value' or brightness value
    :param brightnessMax: maximum 'value' or brightness value
    :param saturationMin: minimum saturation
    :param saturationMax: maximum saturation
    :param invert_hue: inverts the hue threshold to exclude anything within the thresholds
    :return: returns a grayscale image
    '''
    blue = image[:, :, 0].astype(np.float32)
    green = image[:, :, 1].astype(np.float32)
    red = image[:, :, 2].astype(np.float32)

    chanSum = red + green + blue
    chanSum = np.where(chanSum == 0, 1, chanSum)

    b = blue / chanSum
    g = green / chanSum
    r = red / chanSum

    imgOut = 255 * (2 * g - r - b)
    imgOut = np.where(imgOut < 0, 0, imgOut)
    imgOut = np.where(imgOut > 255, 255, imgOut)

    imgOut = imgOut.astype('uint8')

    hsvThresh, _ = hsv(image,
                       hueMin=hueMin, hueMax=hueMax,
                       brightnessMin=brightnessMin, brightnessMax=brightnessMax,
                       saturationMin=saturationMin, saturationMax=saturationMax,
                       invert_hue=invert_hue)
    imgOut = hsvThresh & imgOut
    # cv2.imshow('exhu', imgOut)

    return imgOut

def exgr(image):
    '''
    performs the ExGR algorithm on the input image
    :param image: image as a BGR array (i.e. opened with opencv not PIL)
    :return: returns a grayscale image
    '''
    green = image[:, :, 1].astype(np.float32)
    red = image[:, :, 2].astype(np.float32)

    exgImg = exg(image)
    imgOut = exgImg - (1.4 * red - green)

    imgOut = np.clip(imgOut, 0, 255)
    imgOut = imgOut.astype('uint8')

    return imgOut

def hsv(image,
        hueMin=30,
        hueMax=90,
        brightnessMin=10,
        brightnessMax=220,
        saturationMin=30,
        saturationMax=255,
        invert_hue=False):
    '''
    Performs an HSV thresholding operation on the input image
    :param image: image as a BGR array (i.e. opened with opencv not PIL)
    :param hueMin: minimum hue threshold
    :param hueMax: maximum hue threshold
    :param brightnessMin: minimum 'brightness' or 'value' threshold
    :param brightnessMax: maximum 'brightness' or 'value' threshold
    :param saturationMin: minimum saturation threshold
    :param saturationMax: maximum saturation threshold
    :param invert_hue: inverts the hue threshold to exclude anything within the thresholds
    :return: returns a binary image and boolean thresholded or not
    '''
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue = image[:, :, 0]
    sat = image[:, :, 1]
    val = image[:, :, 2]

    hueThresh = cv2.inRange(hue, hueMin, hueMax)
    satThresh = cv2.inRange(sat, saturationMin, saturationMax)
    valThresh = cv2.inRange(val, brightnessMin, brightnessMax)

    # allow users to select purple/red colour ranges by excluding green
    if invert_hue:
        hueThresh = cv2.bitwise_not(hueThresh)

    # cv2.imshow('hue', hueThresh)
    # cv2.imshow('sat', satThresh)
    # cv2.imshow('val', valThresh)

    outThresh = satThresh & valThresh & hueThresh
    # cv2.imshow('HSV Out', outThresh)
    return outThresh, True

# for NIR images only
def gndvi(image):
    """
    Takes an image and processes it using GNDVI. Returns a single channel grayscale scaled output.
    :return:
    """
    # using array slicing to split into channel
    green = image[:, :, 1].astype(np.float32)
    NIR = image[:, :, 2].astype(np.float32)

    imgOut = (NIR - green) / (NIR + green)
    imgOut = cv2.normalize(imgOut, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    imgOut = imgOut.astype('uint8')
    cv2.imshow('gndvi', imgOut)
    return imgOut


# Other vegetation indices are listed here, but have NOT been tested.
def veg(image):
    blue = image[:, :, 0].astype(np.float32)
    green = image[:, :, 1].astype(np.float32)
    red = image[:, :, 2].astype(np.float32)

    imgOut = green / ((red ** 0.667) * (blue ** 0.333))
    imgOut = cv2.normalize(imgOut, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    imgOut = np.clip(imgOut, 0, 255)
    imgOut = imgOut.astype('uint8')

    return imgOut

def cive(image):
    blue = image[:, :, 0].astype(np.float32)
    green = image[:, :, 1].astype(np.float32)
    red = image[:, :, 2].astype(np.float32)

    imgOut = 0.441 * red - 0.881 * green + 0.385 * blue + 18.78745
    #imgOut = cv2.normalize(imgOut, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    imgOut = np.clip(imgOut, 0, 255)
    imgOut = imgOut.astype('uint8')

    return imgOut

def clahe_sat_val(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue = image[:, :, 0]
    sat = image[:, :, 1]
    val = image[:, :, 2]

    clahe = cv2.createCLAHE(clipLimit=20, tileGridSize=(64,64))
    satCL = clahe.apply(sat)
    valCL = clahe.apply(val)

    claheImage = cv2.merge([hue, satCL, valCL])
    claheImage = cv2.cvtColor(claheImage, cv2.COLOR_HSV2BGR)
    #cv2.imshow('CLAHE', claheImage)
    return claheImage

def dgci(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    hue = image[:, :, 0].astype(np.float32)
    sat = image[:, :, 1].astype(np.float32)
    val = image[:, :, 2].astype(np.float32)

    np.seterr(divide='ignore', invalid='ignore')
    imgOut = ((hue - 60)/(60 + (1 - sat) + (1 - val)))/3

    imgOut = imgOut.astype('uint8')
    imgOut = cv2.normalize(imgOut, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

    return imgOut
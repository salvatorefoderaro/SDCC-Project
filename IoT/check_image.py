import cv2
import glob
import copy
import numpy as np
import PIL.Image as Image
from array import array
from flask import Flask, request
import os
import base64
from pprint import pprint

# Global Variables

reference_image = cv2.imread("img/002.jpeg") # Reference image
dir = 'resources/images/0*.jpeg'

KEYPOINT_TOTAL_AREA = 0
IMAGE_TOTAL_AREA = 0

# Overall filter values to isolate for sick leaves + FPs
LABmin = np.array([68, 110, 138], np.uint8)
LABmax = np.array([255, 162, 255], np.uint8)

# Range filter values for healthy leaves
LABmin_healthy = np.array([0, 83, 124], np.uint8)
LABmax_healthy = np.array([255, 129, 188], np.uint8)

# Range filter values for terrain
LABmin_terrain = np.array([0, 129, 0], np.uint8)
LABmax_terrain = np.array([255, 255, 148], np.uint8)

# Range filter values for yellow leaves and tags (FPs)
HSVmin_yellow = np.array([14, 70, 154], np.uint8)
HSVmax_yellow = np.array([33, 255, 255], np.uint8)

app = Flask(__name__)                   # Create the Flask app


def stackingWindows():
    """
    Stacks the 4 panels that represent the keypoints of
    the filtering pipeline
    """
    space = 50
    offset = 70
    cv2.moveWindow("Original image", space, space)
    cv2.moveWindow("Keypoints original", space, hsize + space + offset)
    cv2.moveWindow("Keypoints Dark", wsize + space, hsize + space + offset)


def filterNotInRange(frame, min, max, colorMode):
    """
    Filters the pixel that are NOT in the specified color
    """

    tempFrame = cv2.cvtColor(frame, colorMode)

    mask = cv2.inRange(tempFrame, min, max)

    filtered_frame = cv2.bitwise_and(frame, frame, mask=mask)

    return filtered_frame


def closing(img, kernel):
    """
    Dilatation followed by erosion, fills small holes in image
    based on kernel size.
    """
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)


def opening(img, kernel):
    """
    Erosion followed by dilatation, deletes spots on background
    based on kernel size.
    """
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)


def differentialNode(input, filter):
    return cv2.subtract(input, filter)


def filteringEngine(original, debug=False):
    """
    Main filtering pipeline for a frame.
    """
    processedImage1 = filterNotInRange(original, LABmin_healthy, LABmax_healthy, cv2.COLOR_BGR2LAB)
    processedImage2 = filterNotInRange(original, LABmin_terrain, LABmax_terrain, cv2.COLOR_BGR2LAB)
    processedImage3 = filterNotInRange(original, HSVmin_yellow, HSVmax_yellow, cv2.COLOR_BGR2HSV)

    sum1 = cv2.add(processedImage1, processedImage2)
    sub1 = differentialNode(original, sum1)

    processedImage = filterNotInRange(sub1, LABmin, LABmax, cv2.COLOR_BGR2LAB)

    kernel = np.ones((6, 6), np.uint8)
    temp = closing(processedImage, kernel)

    kernel = np.ones((3, 3), np.uint8)
    out = opening(temp, kernel)

    return out


def blob_detector(filtered_frame, original_frame):
    """
    Detects blobs. Uses as reference image for finding blobs filtered_frame
    and draws red circles in original frame.
    """

    KEYPOINT_TOTAL_AREA = 0
    # create a bi-color image.
    hsv = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2HSV)
    _, saturation, _ = cv2.split(hsv)
    _, thresholded = cv2.threshold(saturation, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresholded = cv2.bitwise_not(thresholded)

    # Setup SimpleBlobDetector parameters, to detect disease zone
    params = cv2.SimpleBlobDetector_Params()

    params.filterByConvexity = False
    params.filterByInertia = False
    params.filterByArea = False

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(thresholded)
    
    for keyPoint in keypoints:
        ray = keyPoint.size
        keypoint_area = int(3.14*ray*ray)
        KEYPOINT_TOTAL_AREA = KEYPOINT_TOTAL_AREA + keypoint_area

    IMAGE_TOTAL_AREA = original_frame.shape[0] * original_frame.shape[1]

    # Draw detected blobs as red circles.
    keypointsOriginal = cv2.drawKeypoints(original_frame, keypoints, np.array([]), (0, 0, 255),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return keypointsOriginal, KEYPOINT_TOTAL_AREA, IMAGE_TOTAL_AREA


def color_transfer(source, target, clip=True, preserve_paper=True):
    """
    Transfers the color distribution from the source to the target
    image using the mean and standard deviations of the L*a*b*
    color space.
    """
    # Convert the images from the RGB to L.A.B color space (Particular color space), being
    # Sure to utilizing the floating point data type (32 bits cause of OpenCV)
    source = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype("float32")
    target = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype("float32")

    # Compute LAB color statistics (mean value and standard dev) for the source and target images
    # L for the lightness from black (0) to white (100), a from green (−) to red (+)
    # and b from blue (−) to yellow (+)
    (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = image_stats(source)
    (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = image_stats(target)

    # Subtract the means from the target image
    (l, a, b) = cv2.split(target)
    l -= lMeanTar
    a -= aMeanTar
    b -= bMeanTar

    if preserve_paper:
        # Scale by the standard deviations using paper proposed factor
        l = (lStdTar / lStdSrc) * l
        a = (aStdTar / aStdSrc) * a
        b = (bStdTar / bStdSrc) * b
    else:
        # Scale by the standard deviations using reciprocal of paper proposed factor
        l = (lStdSrc / lStdTar) * l
        a = (aStdSrc / aStdTar) * a
        b = (bStdSrc / bStdTar) * b

    # Add in the source mean
    l += lMeanSrc
    a += aMeanSrc
    b += bMeanSrc

    # Clip/scale the pixel intensities to [0, 255] if they fall outside this range
    l = _scale_array(l, clip=clip)
    a = _scale_array(a, clip=clip)
    b = _scale_array(b, clip=clip)

    # merge the channels together and convert back to the RGB color
    transfer = cv2.merge([l, a, b])
    transfer = cv2.cvtColor(transfer.astype("uint8"), cv2.COLOR_LAB2BGR)

    return transfer


def image_stats(image):
    """
    Get the color statistics of the image
    """
    # Compute the mean and standard deviation of each channel
    (l, a, b) = cv2.split(image)
    (lMean, lStd) = (l.mean(), l.std())
    (aMean, aStd) = (a.mean(), a.std())
    (bMean, bStd) = (b.mean(), b.std())

    # Return the color statistics
    return (lMean, lStd, aMean, aStd, bMean, bStd)


def _min_max_scale(arr, new_range=(0, 255)):
    """
    Perform min-max scaling to a NumPy array
    """
    # Get array's current min and max
    mn = arr.min()
    mx = arr.max()

    # Check if scaling needs to be done to be in new_range
    if mn < new_range[0] or mx > new_range[1]:
        # Perform min-max scaling
        scaled = (new_range[1] - new_range[0]) * (arr - mn) / (mx - mn) + new_range[0]
    else:
        # If already in range return array
        scaled = arr

    return scaled


def _scale_array(arr, clip=True):
    """
    Trim NumPy array values to be in [0, 255] range with option of
    clipping or scaling.
    """

    if clip:
        scaled = np.clip(arr, 0, 255)
    else:
        scale_range = (max([arr.min(), 0]), min([arr.max(), 255]))
        scaled = _min_max_scale(arr, new_range=scale_range)

    return scaled

def convert_image_to_bytearray(path):
    with open(path, "rb") as image:
        encoded_string = base64.b64encode(image.read())
    return encoded_string

def convert_bytearray_to_image(path, array):
    with open(path, "wb") as fh:
        fh.write(array.decode('base64'))
        fh.close()
    return fh


# REST API for disease detection of leaf
def disease_detection(image_path, reference_image_path):
    """
    Execute the disease detection method
    """
    data = {}
    imageScaleFactor = 45
    KEYPOINT_TOTAL_AREA = 0
    IMAGE_TOTAL_AREA = 0
    THRESHOLD_VALUE = 1 # Needs to be less or equal then 20

    original = cv2.imread(image_path)

    # Resize the image (16:9)
    hsize = 9 * imageScaleFactor
    wsize = 16 * imageScaleFactor
    original = cv2.resize(original, (wsize, hsize))

    reference_image_cv2 = cv2.imread(reference_image_path)
    color_corrected = color_transfer(reference_image_cv2, original)
    processedImage = filteringEngine(color_corrected)

    # Deep copies of processedImage
    temp_1 = copy.deepcopy(processedImage)

    keypointsOriginal, KEYPOINT_TOTAL_AREA, IMAGE_TOTAL_AREA = blob_detector(temp_1, original)
    im = Image.fromarray(keypointsOriginal)
    im.save("keypoint_image.jpeg")

    perc = 100 * KEYPOINT_TOTAL_AREA / IMAGE_TOTAL_AREA
    if THRESHOLD_VALUE <= perc <= 20:
        data["keypoints_image"] = convert_image_to_bytearray("keypoint_image.jpeg")
        data["message"] = "Attention, medium level of risk"
    elif 21 <= perc <= 100:
        data["keypoints_image"] = convert_image_to_bytearray("keypoint_image.jpeg")
        data["message"] = "Attention, high level of risk"
    
    os.remove("keypoint_image.jpeg", dir_fd=None)
    return data

@app.route('/set_comparison_image', methods = ['POST', 'GET'])
def set_comparison_image():
    """
    Set a comparison image to compare it with the image that present disease
    """
    if request.method == 'POST':
        args = request.get_json()
        try:
            ref_image = args.get("ref_image")
        except Exception:
            ref_image = None
            print("Reference image is missing")
        
        data = {"success": False}
        if ref_image:
            try:
                f = open('/resources/images/ref_image.jpeg', 'wb')
                f.write(bytearray(ref_image))
                f.close()
                data["success"] = True
            except Exception as e:
                print(e)
        return data
    return "You should use a POST method"

if __name__ == "__main__":
    pprint(disease_detection("img/003.jpeg"))

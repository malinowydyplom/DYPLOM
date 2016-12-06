#importujemy potrzebne biblioteki
#import the necessary packages
from pyimagesearch.shapedetector import ShapeDetector
import argparse
import imutils
import cv2

#construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
args = vars(ap.parse_args())

#wczytanie obrazu i zmniejszenie go, aby ksztalty byly
#rozpoznane dokładniej
#load the image and resize it to a smaller factor so that
#the shapes can be approximated better
image = cv2.imread(args["image"])
resized = imutils.resize(image, width=300)
ratio = image.shape[0] / float(resized.shape[0])

#konwersa obrazu do odcieni szarosci oraz lekko rozmywamy
#convert the resized image to grayscale, blur it slightly,
#and threshold it
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

#znajdujemy kontury na obrazie i rozpoczynamy szukanie ksztaltow
#find contours in the thresholded image and initialize the
#shape detector
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if imutils.is_cv2() else cnts[1]
sd = ShapeDetector()

#petla ilosci konturow
#loop over the contours
for c in cnts:
	#zaznaczamy srodki konturow i wykrywamy ich nazwy
	#compute the center of the contour, then detect the name of the
	#shape using only the contour
	M = cv2.moments(c)
	cX = int((M["m10"] / (0.00001+M["m00"])) * ratio)
	cY = int((M["m01"] / (0.00001+M["m00"])) * ratio)
	shape = sd.detect(c)
	
	#zmieniamy kontury do pierwotnego rozmairu obrazu i rysujemy je
	#multiply the contour (x, y)-coordinates by the resize ratio,
	#then draw the contours on the image
	c = c.astype("float")
	c *= ratio
	c = c.astype("int")
	cv2.drawContours(image, [c], -1, (0, 255, 0), 2)

	#wyswietlenie koncowego obrazu
	#show the output image
	cv2.imshow("Image", image)
	cv2.waitKey(0)

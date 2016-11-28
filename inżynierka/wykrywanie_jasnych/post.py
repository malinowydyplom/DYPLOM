# importujemy potrzebne biblioteki
from picamera.array import PiRGBArray
from picamera import PiCamera
from imutils import contours
from skimage import measure
import numpy as np
import imutils
import time
import cv2
import argparse


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
args = vars(ap.parse_args())

# load the video
camera = cv2.VideoCapture(args["video"])

# keep looping
while True:
    (grabbed, frame)=camera.read()

    if not grabbed:
        break

    #konwertujemy obraz w skalę szarości i rozmywamy go

    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)

    #operacja progowa na obrazie w celu odkrycia jasnych regionów
    #na rozmytym obrazie
        
    thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)[1]

    #przeprowadzamy serię erozji i dylatacji w celu usunięcia
    #wszystkich małych szumów
        
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=4)

    #przeprowadzamy analizę na obrazie po dokonanej operacji progowej
    #następnie inicjalizujemy maskę do przechowywania tylko
    #wystarczająco dużych elementów
        
    labels = measure.label(thresh, neighbors=8, background=0)
    mask = np.zeros(thresh.shape, dtype="uint8")

    #rozpoczynamy pętlę po unikalnych komponentach
        
    for label in np.unique(labels):

            #jeśli to element tła,ignorujemy go
                
            if label == 0:
                    continue

            #w przeciwnym wypadku, konstruujemy maskę i liczymy piksele
                
            labelMask = np.zeros(thresh.shape, dtype="uint8")
            labelMask[labels == label] = 255
            numPixels = cv2.countNonZero(labelMask)

            #jeśli liczba pixeli w elemencie jest wystarczająco duża
            #dodajemy do naszej maski
                
            if numPixels > 300:
                    mask = cv2.add(mask, labelMask)

    #znajdź kontury w masce, następnie posortuj je od lewej do prawej
                    
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    print(cnts)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    if cnts:

            cnts = contours.sort_contours(cnts)[0]
            # pętlę przez kontury
            for (i, c) in enumerate(cnts):
                    #zaznaczamy jasne miejsca na obrazie
                    (x, y, w, h) = cv2.boundingRect(c)
                    ((cX, cY), radius) = cv2.minEnclosingCircle(c)
                    cv2.circle(frame, (int(cX), int(cY)), int(radius),(0, 0, 255), 3)
                    cv2.putText(frame, "MARKER NUMER {}".format(i + 1), (x, y - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

    #wyświetlamy klatkę
        
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key==ord('q'):
        break

camera.release()
cv2.destroyAllWindows()




    

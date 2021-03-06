#importujemy potrzebne biblioteki
from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
from imutils import contours
from skimage import measure
import numpy as np
import imutils
import time
import cv2
from math import atan, pi
from pyimagesearch.shapedetector import ShapeDetector


#tworzymy wątek streamu wideo, pozwalamy kamerze na rozgrzanie się
#zaczynamy odliczanie FPS
#create video stream, allow camera to warmup and start counting FPS

print('[INFORMACJA] pobieranie klatek z modułu ''picamera''...')
vs=PiVideoStream().start()
time.sleep(2.0)

#tworzymy pętlę przez klatki
#loop over frames
while True:
    #pobieramy klatkę ze streamu wideo
    #grab a frame from stream
    frame=vs.read()
    

    #konwertujemy obraz w skalę szarości i rozmywamy go
    #convert image to grayscale
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred=cv2.GaussianBlur(gray, (11,11), 0)

    #operacja progowa na obrazie w celu odkrycia jasnych regionów
    #treshold the image to reveal light regions in image
    thresh=cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)[1]

    #przeprowadzamy serię erozji i dylatacji w celu usunięcia małych szumów
    #perform series of erosions and dilatations to remove small noises
    thresh=cv2.erode(thresh, None, iterations=2)
    thresh=cv2.dilate(thresh, None, iterations=4)

    #analizujemy obraz oraz inicjujemy maskę do przechowywania tylko
    #wystarczająco dużych elementów
    # perform a connected component analysis on the thresholded
    # image, then initialize a mask to store only the "large"
    # components
    labels = measure.label(thresh, neighbors=8, background=0)
    mask = np.zeros(thresh.shape, dtype='uint8')

    #analizujemy komponenty charakterystyczne
    #loop over the unique components
    for label in np.unique(labels):
        #jeśli to element tła, ignorujemy
        #if this is the background label,ignore itd
        if label==0:
            continue
        #w przeciwnym razie konstruujemy maskę oraz sprawdzamy liczbę pikseli
        #otherwise, construct the label mask and count number of pixels

        labelMask=np.zeros(thresh.shape, dtype='uint8')
        labelMask[labels==label]=255
        numPixels=cv2.countNonZero(labelMask)

        #jeśli liczba pikseli elementu jest wystarczająco duża
        #to dodajemy do naszej maski
        # if the number of pixels in the component is sufficiently
	# large, then add it to our mask of "large blobs"
        if numPixels>400:
            mask=cv2.add(mask, labelMask)

    #znajdź kontury w masce a następnie posortuj je od lewej do prawej
    #find the contours in the mask and then sort them
    cnts=cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    
    cnts=cnts[0] if imutils.is_cv2() else cnts[1]
    sd=ShapeDetector()
    

    #inucjujemy listy do przechowywania współrzędnych środków konturów
    #initiate lists for gathering coordinates of contours centroids
    list_rectangle=[]
    #list_triangle=[]
    list_circle=[]

    #tworzymy pętlę poprzez kontury
    #loop over the contours
    for (i,c) in enumerate(cnts):

        #zapewniamy wykrycie jedynie 3 markerów
        #break if more than 3 contours appears
        if i >= 3:
            break
        M=cv2.moments(c)
        cX=int((M['m10']/(M['m00'])))
        cY=int((M['m01']/(M['m00'])))
        shape=sd.detect(c)

        #rysujemy kontury z nazwą kształtu
        c=c.astype('float')        
        c=c.astype('int')
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
        cv2.circle(frame, (int(cX), int(cY)), int(1), (0,255,0), 2)

        if shape=="rectangle":
            list_rectangle.append(cX)
            list_rectangle.append(cY)        
            cv2.putText(frame, "Marker nr 1",(cX, cY-20),
            cv2.FONT_HERSHEY_PLAIN, 0.45, (0, 0, 255), 1)
        #elif shape=="triangle":
        #    list_triangle.append(cX)
         #   list_triangle.append(cY)
          #  cv2.putText(frame, "Marker nr 2",(cX, cY-20),
           # cv2.FONT_HERSHEY_PLAIN, 0.45, (0, 0, 255), 1)
        elif shape=="circle":
            list_circle.append(cX)
            list_circle.append(cY)        
            cv2.putText(frame, "Marker nr 3",(cX, cY-20),
            cv2.FONT_HERSHEY_PLAIN, 0.45, (0, 0, 255), 1)

        if len(list_circle)==4 and len(list_rectangle)==2:
            cv2.line(frame,(int(list_rectangle[0]),int(list_rectangle[1])),
                     (int(list_circle[0]),int(list_circle[1])), (0,0,255), 1, 8, 0)

            cv2.line(frame,(int(list_rectangle[0]),int(list_rectangle[1])),
                     (int(list_circle[2]),int(list_circle[3])), (0,0,255), 1, 8, 0)
            

    cv2.imshow('Image', frame)
    key=cv2.waitKey(1)&0xFF
    if key==ord('q'):
        break

cv2.destroyAllWindows()
vs.stop()
        
        

        

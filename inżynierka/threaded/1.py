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


#tworzymy wątek streamu wideo, pozwalamy kamerze na rozgrzanie się
#zaczynamy odliczanie FPS
#create video stream, allow camera to warmup and start counting FPS

print('[INFORMACJA] pobieranie klatek z modułu ''picamera''...')
vs=PiVideoStream(resolution=(320, 240)).start()
time.sleep(2.0)
fps=FPS().start()

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
    thresh=cv2.threshold(blurred, 230, 255, cv2.THRESH_BINARY)[1]

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
    if cnts:
        cnts=contours.sort_contours(cnts)[0]

        #inucjujemy listy do przechowywania współrzędnych środków konturów
        #initiate lists for gathering coordinates of contours centroids
        listX=[]
        listY=[]

        #tworzymy pętlę poprzez kontury
        #loop over the contours
        for (i,c) in enumerate(cnts):

            #zapewniamy wykrycie jedynie 3 markerów
            #break if more than 3 contours appears
            if i >= 3:
                break

            #zaznaczamy jasne regiony na obrazie
            #draw the bright spot on the image
            (x, y, w, h)=cv2.boundingRect(c)
            ((cX, cY), radius)=cv2.minEnclosingCircle(c)
            cv2.circle(frame, (int(cX), int(cY)), int(radius),(0, 0, 255), 1)
        
            #tworzymy środek okręgu
            #draw the centroid of circle
            cv2.circle(frame, (int(cX), int(cY)), int(1),(0, 0, 255), 1)
            cv2.putText(frame, "Marker nr.{}".format(i+1),(x, y-15),
            cv2.FONT_HERSHEY_PLAIN, 0.45, (0, 0, 255), 1)

            #tworzymy listę środków wykrytych punktów
            #create lists of detected contours centroids
            listX.append(cX)
            listY.append(cY)                      
            
            #łączymy środki kolejnych markerów
            #connect centroids of next contours
            if i>0:
                cv2.line(frame,(int(listX[i]),int(listY[i])),(int(listX[i-1]),
                                                                int(listY[i-1])),(255,0,0),1)
            
        #obliczamy kąt pomiędzy prostymi i wyświetlamy go
        #zmienna tymczasowa do rozmiaru listy
        #measuring angles between centroids
        list_length=len(listX)

        if list_length >= 2:
            angle1=int(atan((listX[0]-listX[1])/(listY[0]-listY[1]))*180/pi+90)
            cv2.putText(frame, "Kat 1: "+str(angle1), (10,10), cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 0, 255), 1)
            pass
        
        if list_length >= 3:
            angle2=int(atan((listaY[1]-listaY[2])/(listaX[2]-listaX[1]))*180/pi)
            cv2.putText(frame, "Kat 2: "+str(angle2), (10,20), cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 0, 255), 1)
            pass        
                     
    #wyświetlamy klatkę
    #show interpolated frame
    res=cv2.resize(frame, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)        
    cv2.imshow("Frame", res)
    key=cv2.waitKey(1) & 0xFF
    if key==ord('q'):
        break

    #uaktualniamy zliczanie FPS
    #update FPS counter
    fps.update()

#zatrzymujemy timer i wyświetlamy informację o FPS
#stop timer and show FPS information
fps.stop()
print('[INFORMACJA] szacowany czas: {:.2f}'.format(fps.elapsed()))
print('[INFORMACJA] przybliżona ilość FPS: {:.2f}'.format(fps.fps()))

cv2.destroyAllWindows()
vs.stop()

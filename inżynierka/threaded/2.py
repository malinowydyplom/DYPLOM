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


#tworzymy wątek streamu wideo, pozwalamy kamerze na rozgrzanie się
#zaczynamy odliczanie FPS

print('[INFORMACJA] pobieranie klatek z modułu ''picamera''...')
vs=PiVideoStream(resolution=(320, 240)).start()
time.sleep(2.0)
fps=FPS().start()

#tworzymy pętlę przez klatki
while True:
    #pobieramy klatkę ze streamu wideo
    frame=vs.read()

    #konwertujemy obraz w skalę szarości i rozmywamy go
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred=cv2.GaussianBlur(gray, (11,11), 0)

    #operacja progowa na obrazie w celu odkrycia jasnych regionów
    thresh=cv2.threshold(blurred, 230, 255, cv2.THRESH_BINARY)[1]

    #przeprowadzamy serię erozji i dylatacji w celu usunięcia małych szumów
    thresh=cv2.erode(thresh, None, iterations=2)
    thresh=cv2.dilate(thresh, None, iterations=4)

    #analizujemy obraz oraz inicjujemy maskę do przechowywania tylko
    #wystarczająco dużych elementów
    labels = measure.label(thresh, neighbors=8, background=0)
    mask = np.zeros(thresh.shape, dtype='uint8')

    #analizujemy komponenty charakterystyczne
    for label in np.unique(labels):
        if label==0:
            continue
        labelMask=np.zeros(thresh.shape, dtype='uint8')
        labelMask[labels==label]=255
        numPixels=cv2.countNonZero(labelMask)

        #jeśli liczba pikseli elementu jest wystarczająco duża
        #to dodajemy do naszej maski
        if numPixels>400:
            mask=cv2.add(mask, labelMask)

    #znajdź kontury w masce a następnie posortuj je od lewej do prawej
    cnts=cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    
    cnts=cnts[0] if imutils.is_cv2() else cnts[1]
    if cnts:
        cnts=contours.sort_contours(cnts)[0]
        #(prevcX, prevcY) = (0, 0)
        lista=[]

        for (i,c) in enumerate(cnts):     
            (x, y, w, h)=cv2.boundingRect(c)
            ((cX, cY), radius)=cv2.minEnclosingCircle(c)
            cv2.circle(frame, (int(cX), int(cY)), int(radius),(0, 0, 255), 1)
        
            #tworzymy środek okręgu
            cv2.circle(frame, (int(cX), int(cY)), int(1),(0, 0, 255), 1)
            cv2.putText(frame, "Marker nr.{}".format(i+1),(x, y-15),
            cv2.FONT_HERSHEY_PLAIN, 0.45, (0, 0, 255), 1)

            #tworzymy listę środków wykrytych markerów
            lista.append((cX,cY))
            
            #łączymy środki kolejnych markerów
            if i>0:
                cv2.line(frame,(int(lista[i]),(int(lista[i-1]),(255,0,0),1)
            #prevcX = int(cX)
            #prevcY = int(cY)
                     
    #wyświetlamy klatkę
    res = cv2.resize(frame, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)        
    cv2.imshow("Wizja", res)
    key=cv2.waitKey(1) & 0xFF
    if key==ord('q'):
        break

    #uaktualniamy zliczanie FPS
    fps.update()

#zatrzymujemy timer i wyświetlamy informację o FPS
fps.stop()
print('[INFORMACJA] szacowany czas: {:.2f}'.format(fps.elapsed()))
print('[INFORMACJA] przybliżona ilość FPS: {:.2f}'.format(fps.fps()))

cv2.destroyAllWindows()
vs.stop()

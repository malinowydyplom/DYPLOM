#import necesarry libraries
from imutils import contours
from skimage import measure
import numpy as np
import imutils
import time
import cv2
from math import acos, pi, sqrt
from pyimagesearch.shapedetector import ShapeDetector
import argparse


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
args = vars(ap.parse_args())

camera=cv2.VideoCapture(args['video'])
if args.get('video', None) is None:
    print('załaduj plik wideo')
    
#loop over frames
while True:
    (grabbed, frame)=camera.read()
    #break after last frame
    if not grabbed:
        break

    #convert image to grayscale
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred=cv2.GaussianBlur(gray, (11,11), 0)

    #treshold the image to reveal light regions in image
    thresh=cv2.threshold(blurred, 160, 255, cv2.THRESH_BINARY)[1]

    #perform series of erosions and dilatations to remove small noises
    thresh=cv2.erode(thresh, None, iterations=2)
    thresh=cv2.dilate(thresh, None, iterations=4)

    # perform a connected component analysis on the thresholded
    # image, then initialize a mask to store only the "large"
    # components
    labels = measure.label(thresh, neighbors=8, background=0)
    mask = np.zeros(thresh.shape, dtype='uint8')

    #loop over the unique components
    for label in np.unique(labels):
        #if this is the background label,ignore itd
        if label==0:
            continue
        #otherwise, construct the label mask and count number of pixels
        labelMask=np.zeros(thresh.shape, dtype='uint8')
        labelMask[labels==label]=255
        numPixels=cv2.countNonZero(labelMask)
        
        # if the number of pixels in the component is sufficiently
	# large, then add it to our mask of "large blobs"
        if numPixels>300:
            mask=cv2.add(mask, labelMask)

    #define function findContours as cnts
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
    cnts=cnts[0] if imutils.is_cv2() else cnts[1]

    #initiate shape detection
    sd=ShapeDetector()
    
    #initiate lists for gathering coordinates of contours centroids
    list_rectangle=[]
    list_circle=[]

    #loop over the contours
    for (i,c) in enumerate(cnts):
        #break if more than 3 contours appears
        if i >= 3:
            break
        #compute moment of contours and centres
        M=cv2.moments(c)
        cX=int((M['m10']/(M['m00'])))
        cY=int((M['m01']/(M['m00'])))
        shape=sd.detect(c)

	#draw contours
        c=c.astype('float')        
        c=c.astype('int')
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
        cv2.circle(frame, (int(cX), int(cY)), int(1), (0,255,0), 2)

        #create lists containing centres coordinates
        if shape=="rectangle":
            list_rectangle.append(cX)
            list_rectangle.append(cY)        
           
        elif shape=="circle":
            list_circle.append(cX)
            list_circle.append(cY)        

	#give names of points coordinates and conect them
        if len(list_circle)==4 and len(list_rectangle)==2:
            c1_px=list_circle[0]
            c1_py=list_circle[1]
            c2_px=list_circle[2]
            c2_py=list_circle[3]
            rec_px=list_rectangle[0]
            rec_py=list_rectangle[1]

            #draw lines connecting centres of contours
            cv2.line(frame,(int(rec_px),int(rec_py)),
                     (int(c1_px),int(c1_py)), (0,0,255), 1, 8, 0)

            cv2.line(frame,(int(rec_px),int(rec_py)),
                     (int(c2_px),int(c2_py)), (0,0,255), 1, 8, 0)

	    #count length and angle between arms(lines)
            d12 = sqrt((rec_px-c1_px)**2+(rec_py-c1_py)**2)
            d23 = sqrt((rec_px-c2_px)**2+(rec_py-c2_py)**2)
            d13 = sqrt((c2_px-c1_px)**2+(c2_py-c1_py)**2)
            rad = acos(((d12**2) + (d23**2) - (d13**2))/(2*d12*d23))*(180/pi)
<<<<<<< HEAD

            #round value of given rad up to second decimal digit
            #then show value on the upper left corner of the output image
=======
>>>>>>> ec4e3d0ae138c5c2a1bbf8aa9ccb613d8a892c8f
            rad=round(rad, 2)
            cv2.putText(frame, "Kat: "+str(rad), (10,20), cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 0, 255), 1)
            pass  
            
    #show analised image
    cv2.imshow('Image', frame)
    key=cv2.waitKey(1)&0xFF

    #close the program after pressing "q" button
    if key==ord('q'):
        break

#release the video retrieving function and close all windows
camera.release()
cv2.destroyAllWindows()



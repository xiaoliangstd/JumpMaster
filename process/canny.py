import cv2 as cv  
import numpy as np 

img = cv.imread('57.png',1)

img1 = cv.Canny(img,50,100)

canvas  = np.copy(img)

img,contours,hed = cv.findContours(img1, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

for c in contours:
    if cv.contourArea(c)>800:
        
        x,y,w,h = cv.boundingRect(c)
        if x<140:
            cv.rectangle(canvas,(x,y),(x+w,y+h),(255,255,0),5)
            cv.circle(canvas,(int(x+w/2),int(y+h/2)),5,(0,0,255),-1)
            cv.imshow('canvas',canvas)

cv.imshow('img1',img1)
#cv.imshow('img',img)
cv.waitKey(0)
cv.destroyAllWindows()


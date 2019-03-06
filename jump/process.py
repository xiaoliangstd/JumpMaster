import cv2 as cv 
import numpy as np 
lower = np.array([105,25,45])
upper = np.array([135,125,130])
kernel = np.ones((5,5),np.uint8)
class jumpmaster:

    def __init__(self):
        pass

    def findChess(self,img,canvas):
        hsv = cv.cvtColor(img,cv.COLOR_BGR2HSV)
        bin_img = cv.inRange(hsv,lower,upper)
        dliate = cv.dilate(bin_img,kernel,iterations = 2)
        erode = cv.erode(dliate,kernel,iterations = 1)
        bin_im,contours,hierarchy = cv.findContours(erode,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x,y,w,h = cv.boundingRect(cnt)
            area = w*h
            
            if area>5000 and area < 5700: # area filter  
                cv.rectangle(canvas,(x,y),(x+w,y+h),color = (0,0,255),thickness = 6)
                print(w)
                print(h)
                #print("chess position is : x:{},y:{}".format(x+w/2,y+h))
                return canvas,x+w/2,y+h
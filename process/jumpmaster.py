import cv2 as cv 
import numpy as np 


color_lower = np.int32([105,25,45])
color_upper = np.int32([135,125,130])


def draw_canvas():

    global x
    global y
    global w 
    global h 
    global img
    canvas = np.copy(img)

    cv.rectangle(canvas,(x,y),(x+w,y+h),(255,0,0),5)
    cv.circle(canvas,(int(x+w/2),y+h),5,(0,0,255),-1)

    cv.imshow('canvas',canvas)





def openAndclose():
    openOperation()
    closeOperation()


def openOperation():
    
    global kernel
    global dilateImage

    kernel = np.ones((5,5),np.uint8)
    erodeImage = cv.erode(binImage,kernel,iterations = 1)
    dilateImage = cv.dilate(erodeImage,kernel,iterations = 1)



def closeOperation():
    
    global erode1Image

    dilate1Image = cv.dilate(dilateImage,kernel,iterations = 2)
    erode1Image = cv.erode(dilate1Image,kernel,iterations = 2)
    
     


def getContours():
    
# to getcontours must assure the binimage only contain the object
# otherwise you must filtrate the max contours

    global erode1Image
    global x
    global y
    global w 
    global h 

    erode1Image,contours,hierarchy = cv.findContours(erode1Image,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)

# the output contours is a python list contain all the contour in the image 
# so if we want to draw rectangle, we must traversal the python list 
# and then pass the contour to function cv.boundingRect get the 
# coordinate of the rectangle and then  draw it up
    for c in contours:
        x,y,w,h = cv.boundingRect(c)
        #thresImage1 = cv.rectangle(erode1Image,(x,y),(x+w,y+h),(255,255,255),2)
        #thresImage = cv.circle(thresImage1,(int(x+w/2),y+h),5,(0,255,0),-1)
    #cv.imshow("thersImage",thresImage)

def main():
    
    global img

    loop = np.arange(41,68)
    for i in loop:
        img = cv.imread(str(i)+'.png',-1)
        getBinImage()
        openAndclose()
        getContours()
        draw_canvas()

def getBinImage():
    
    global img
    global binImage
    
    img_hsv = cv.cvtColor(img,cv.COLOR_BGR2HSV)
    binImage = cv.inRange(img_hsv,color_lower,color_upper)

    
    #cv.imshow('oringin',img)

    cv.waitKey(500)
    
   



if __name__ == '__main__':
    main()


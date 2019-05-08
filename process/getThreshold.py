import cv2 as cv 
import numpy as np



def updateImage():
    
    global imgHsv
    
    imgBin = cv.inRange(imgHsv,lower_th,up_th)
    cv.imshow('imgBin',imgBin)


def updateThreshold(x):

    global lower_th
    global up_th

    minH = cv.getTrackbarPos('minH','img')
    maxH = cv.getTrackbarPos('maxH','img')
    minS = cv.getTrackbarPos('minS','img')
    maxS = cv.getTrackbarPos('maxS','img')
    minV = cv.getTrackbarPos('minV','img')
    maxV = cv.getTrackbarPos('maxV','img')

    lower_th = np.int32([minH,minS,minV])
    up_th = np.int32([maxH,maxS,maxV])

    updateImage()
    print(lower_th)
    print(up_th)




def main(img):
    
    global imgHsv

    cv.namedWindow('img')
    imgHsv = cv.cvtColor(img,cv.COLOR_BGR2HSV)
    cv.createTrackbar('minH','img',0,255,updateThreshold)
    cv.createTrackbar('maxH','img',0,255,updateThreshold)
    cv.setTrackbarPos('maxH','img',255)
    cv.createTrackbar('minS','img',0,255,updateThreshold)
    cv.createTrackbar('maxS','img',0,255,updateThreshold)
    cv.setTrackbarPos('maxS','img',255)
    cv.createTrackbar('minV','img',0,255,updateThreshold)
    cv.createTrackbar('maxV','img',0,255,updateThreshold)
    cv.setTrackbarPos('maxV','img',255)

    cv.imshow("img",img)
    
    while cv.waitKey(0) != ord('e'):
        continue
        
    
    cv.destroyAllWindows()
    

  107 154 46
  123 247 121  


if __name__ == '__main__':
    
    img = cv.imread('987.png',-1)

    main(img)

import cv2 as cv 
import numpy as np 

def visual(img): 
    global canvas 
    canvas = img
    cv.namedWindow("img.png")
    cv.createTrackbar("Hmax","img.png",0,255,nothing)
    cv.createTrackbar("Hmin","img.png",0,255,nothing)
    cv.createTrackbar("Smax","img.png",0,255,nothing)
    cv.createTrackbar("Smin","img.png",0,255,nothing)
    cv.createTrackbar("Vmax","img.png",0,255,nothing)
    cv.createTrackbar("Vmin","img.png",0,255,nothing)
    cv.imshow("img.png",img)

    


def nothing(x):
    global lower 
    global upper
    Hmin = cv.getTrackbarPos("Hmin","img.png")
    Hmax = cv.getTrackbarPos("Hmax","img.png")
    Smax = cv.getTrackbarPos("Smax","img.png")
    Smin = cv.getTrackbarPos("Smin","img.png")
    Vmax = cv.getTrackbarPos("Vmax","img.png")
    Vmin = cv.getTrackbarPos("Vmin","img.png")
    lower = np.int32([Hmin,Smin,Vmin])
    upper = np.int32([Hmax,Smax,Vmax])
    print(lower)
    print(upper)
    update()
    
def update():
    global lower
    global upper
    global canvas
    img_bin = cv.inRange(canvas,lower,upper)
    cv.imshow("bin",img_bin)



if __name__ == "__main__":

    img = cv.imread("1.png",-1)
    hsv_img = cv.cvtColor(img[50:200,0:300],cv.COLOR_BGR2HSV)
    canvas = np.copy(hsv_img)
    visual(hsv_img)
    cv.waitKey(0)
    cv.destroyAllWindows()
   
    
 
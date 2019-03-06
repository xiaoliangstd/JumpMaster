import cv2 as cv 
import numpy as np 
lower = np.array([105,25,45])
upper = np.array([135,125,130])
kernel = np.ones((5,5),np.uint8)
class jumpmaster:

    def __init__(self):
        self.roi = None

    def findChess(self,img,canvas):
        roi = img[300:600,:]
        self.roi = roi
        hsv = cv.cvtColor(roi,cv.COLOR_BGR2HSV)
        bin_img = cv.inRange(hsv,lower,upper)
        dliate = cv.dilate(bin_img,kernel,iterations = 2)
        erode = cv.erode(dliate,kernel,iterations = 1)
        bin_im,contours,hierarchy = cv.findContours(erode,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x,y,w,h = cv.boundingRect(cnt)
            area = w*h
            
            if area>4000 and area < 5700: # area filter  
                cv.rectangle(canvas,(x,y),(x+w,y+h),color = (0,0,255),thickness = 6)
                #print("chess position is : x:{},y:{}".format(x+w/2,y+h))
                return canvas,x+w/2,y+h

    def findBox(self):
        stop = 0
        edges = cv.Canny(self.roi,100,200)
        for r,i in enumerate(edges):
            for c,j in enumerate(i):
                if j == 255:
                    stop = 1
                    break
            if stop == 1: 
                break
        return r,c,self.roi

if __name__ == "__main__":
    img_indx = 0
    while True:
        stop = 0
        
        img = cv.imread("../test_data/"+str(img_indx)+".png",-1)
        resize = cv.resize(img,(700,900))
        roi = resize[300:600,:]
        edges = cv.Canny(roi,100,200)
        for r,i in enumerate(edges):
            for c,j in enumerate(i):
                if j == 255:
                    print(r,c)
                    stop = 1
                    break 
            if stop == 1:
                break
        cv.circle(roi,(c,r),6,(0,0,255),-1)  # why?
        cv.circle(roi,(c,r+50),6,(0,0,255),-1)
        cv.imshow("roi",roi)
        cv.imshow("edge",edges)   
        img_indx +=1         
        key_num = cv.waitKey(0)
        if key_num == ord("n"):
            continue
        if key_num == ord("s"):
            break
    cv.destroyAllWindows()
    
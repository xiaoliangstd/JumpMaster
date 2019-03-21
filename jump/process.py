import cv2 as cv 
import numpy as np 
lower = np.array([105,25,45])
upper = np.array([135,125,130])
kernel = np.ones((5,5),np.uint8)
# use obj is a necessary way to code
# do use 
# api designe  and create api
class jumpmaster:

    def __init__(self):
        self.roi = None
        self.chess_pos = None
        self.box_pos = None
        self.che_wh = None 
        
    def findChess(self,img):
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
                self.chess_pos = (x,y)
                self.che_wh = (w,h)
                #print("chess position is : x:{},y:{}".format(x+w/2,y+h))
                return x+w/2,y+h

    def findBox(self):
        stop = 0
        edges = cv.Canny(self.roi,100,200)
        che_x,che_y = self.chess_pos
        # find box pointe1 x1 
        for s in range(che_y,che_y + 100):
            # find box pointe1 y1
            for d in range(che_x-20,che_x + 90):
                edges[s][d] = 0
        cv.imshow("edgess",edges)
        for r,i in enumerate(edges):
            for c,j in enumerate(i):
                if j == 255:
                    stop = 1
                    self.box_pos = (r,c)
                    break
            if stop == 1: 
                break
        cv.circle(self.roi,(c,r),6,(0,0,255),-1)
        # o is the array data    k is the number
        for k,o in enumerate(edges[r+10]):
            if o == 255:
                #print("x2:",k,"y2:",r+10)
                cv.circle(self.roi,(k,r+10),6,(0,0,255),-1)
                break
        # box pointe two
        
        for q,o in enumerate(edges[r+10][::-1]):
            if o == 255:
                
                cv.circle(self.roi,(700-q,r+10),6,(0,0,255),-1)
                break

        '''
        for q,o in enumerate(edges[r+20,k+10:]):
            this_data = o
            next_data = edges[r+10][q+1]
            if (this_data == 255) and (next_data == 0):
                cv.circle(self.roi,(k+q+10,r+10),6,(0,0,255),-1)
                break
        '''
        cv.imshow('canvas2',self.roi)
        return r,c

    def visual(self):
        canvas = self.roi 
        che_x,che_y = self.chess_pos
        che_w,che_h = self.che_wh
        box_y,box_x = self.box_pos
        cv.line(canvas,(che_x+int(che_w/2),che_y+che_h),(box_x,box_y+50),(0,0,255),5)
        cv.imshow("visual",canvas)

if __name__ == "__main__":
    # follow code use to test api
    img_indx = 0
    jum = jumpmaster()
    while True:
        stop = 0
        img = cv.imread("../test_data/"+str(img_indx)+".png",-1)
        canvas = np.copy(img)
        jum.findChess(img)
        r,c = jum.findBox()
        cv.circle(canvas,(c,r+300),6,(255,0,0),-1)
        cv.imshow("canvas",canvas)
        
        '''
        edges = cv.Canny(roi,100,200)
        cv.circle(roi,(c,r),6,(0,0,255),-1)  # why?
        cv.circle(roi,(c,r+50),6,(0,0,255),-1)
        cv.imshow("roi",roi)
        cv.imshow("edge",edges)  
        '''
        img_indx +=1         
        key_num = cv.waitKey(0)
        if key_num == ord("n"):
            continue
        if key_num == ord("s"):
            break
    cv.destroyAllWindows()
    
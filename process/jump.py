import cv2 as cv
import numpy as np 


class Jumper():
    
    def __init__(self,img):
        
        self.img = img
        self.roi = self.img[250:550,0:600]
        self.imgHsv = None
        self.che_pos = (50,50,50,50)
        self.box_pos = None


        
        self.che_mask = None

        self.color_lower = np.int32([107,154,46])
        self.color_upper = np.int32([123,247,121])
    
    def cal_che_pos(self):
        
        self.imgHsv = cv.cvtColor(self.roi,cv.COLOR_BGR2HSV)
        self.che_mask = cv.inRange(self.imgHsv,self.color_lower,self.color_upper)

        canny_che_img = cv.Canny(self.che_mask,60,150)
        
        


        # morphological processing

        kernel = cv.getStructuringElement(cv.MORPH_RECT,(8,8))
        self.che_mask = cv.morphologyEx(self.che_mask,cv.MORPH_OPEN,kernel)  # noise eliminate
        self.che_mask = cv.morphologyEx(self.che_mask,cv.MORPH_CLOSE,kernel) # connect the head and body

        cv.imshow('che_mask',self.che_mask)
        
        img,contours,hier = cv.findContours(self.che_mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)

        for c in contours:

            (x,y,w,h) = cv.boundingRect(c)
            self.che_pos = (x,y,w,h)
            
        
    
    def cal_box_pos(self):
        
        canny_img = cv.Canny(self.roi,60,150)

        chang,kuan= np.shape(canny_img)

        cx,cy,cw,ch = self.che_pos
        
        # 
        for x1 in np.arange(cx,cx+50):
            for y1 in np.arange(cy-10,cy+70):
                canny_img[y1][x1] = 0 
        
        # mask top point of the box
        for i in np.arange(0,600):
            for d in np.arange(0,300):
                if canny_img[row][clo] != 0:
                    top_point = (i,d)
                    break
        
        
        
        img,contours,hier = cv.findContours(canny_img,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        
        for c in contours:

            x,y,w,h = cv.boundingRect(c)
            
            if abs(x-cx)>50 :
                
                self.box_pos = (x,y,w,h)
                       


    def display(self):

        canvas = np.copy(self.roi)
        
        # draw the chess body
        x,y,w,h = self.che_pos
        cv.rectangle(canvas,(x,y),(x+w,y+h),(255,0,0),5)
        cv.circle(canvas,(int(x+w/2),y+h),5,(0,0,255),-1)

        # draw the box body
        #cv.circle(canvas,(int(bx+bw/2),int(by+bh/2)),5,(0,0,255),-1)



        #cv.imshow('che_mask',self.che_mask)
        cv.imshow('canvas',canvas)
        


if __name__ == "__main__":
    
    a = np.arange(41,68)
    for i in a:

        img = cv.imread(str(i)+'.png',-1)
        jumper = Jumper(img)
        jumper.cal_che_pos()
        jumper.cal_box_pos()
        
        jumper.display()
        k = cv.waitKey(0)
        if k == ord('n'):
            pass
        
        
            

    cv.waitKey(0)
    cv.destroyAllWindows()
    
'''
    cap = cv.VideoCapture(1)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    cv.namedWindow('image_win',flags=cv.WINDOW_NORMAL | cv.WINDOW_KEEPRATIO | cv.WINDOW_GUI_EXPANDED)

    
    
    while(True):

        ret,frame = cap.read()
        jumper = Jumper(frame)

        jumper.cal_che_pos()
        jumper.display()
        

        cv.imshow('window',frame)
        cv.waitKey(10)
        key = cv.waitKey(1)
        if key == ord('q'):
        # 如果按键为q 代表quit 退出程序
            print("程序正常退出...Bye 不要想我哦")
            break
        elif key == ord('c'):
        ## 如果c键按下，则进行图片保存
        # 写入图片 并命名图片为 图片序号.png
            cv.imwrite("987.png", frame)
        
        
cap.release()
# 销毁所有的窗口
cv.destroyAllWindows()
'''

    

from jump.adb import Adb
from jump.process import jumpmaster 
import cv2 as cv 
import numpy as np 
import math
import time

mx = 0
my = 0
ratio = 0.5

def mouse_val(event,x,y,flags,param):
    global mx,my,che_x,che_y,ratio,a

    if event == cv.EVENT_LBUTTONDOWN:
        cv.imwrite("error"+str(a)+".png",img)
        """
        x1 = np.random.randint(550,600)
        y1 = np.random.randint(350,550)
        time = math.sqrt(abs(che_x - x)**2 + abs(che_y - y)**2)
        #print("distance : ",math.sqrt(abs(che_x - x)**2 + abs(che_y - y)**2))
        cal_time = int(time*2.2)
        adb.touch(x1,y1,cal_time)
        """

if __name__ == "__main__":
    
    adb = Adb()
    jmp = jumpmaster()
    
    #mouse_val()
    while True: 
        img = adb.screenshot()   # 发送ADB指令截图 
        cv.imwrite("error11.png",img)
        try:
            che_x,che_y = jmp.findChess(img)
            x,y = jmp.findBox()
            jmp.visual()
            cv.waitKey(1000)
            adb.touch(che_x,che_y,x,y) 
            jmp.index+=1
        except TypeError :
            print(TypeError)
            cv.imwrite("error1.png",img)
            jmp.index+=1
            '''
            cv.imshow("s",erode) # 如果出现错误 在process.py中合适的位置放此语句调试
            cv.waitKey(0)
            '''

            continue 

        cv.waitKey(1000)    

    cv.destroyAllWindows()

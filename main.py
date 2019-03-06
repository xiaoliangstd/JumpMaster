from jump.adb import Adb
from jump.process import jumpmaster 
import cv2 as cv 
import numpy as np 
import math
# mouse like interrupt
# global value  in control stament
mx = 0
my = 0
ratio = 0.5
def mouse_val(event,x,y,flags,param):
    global mx,my,che_x,che_y,ratio
    
    
    if event == cv.EVENT_LBUTTONDOWN:
        x1 = np.random.randint(550,600)
        y1 = np.random.randint(350,550)
        time = math.sqrt(abs(che_x - x)**2 + abs(che_y - y)**2)
        print("distance : ",math.sqrt(abs(che_x - x)**2 + abs(che_y - y)**2))
        cal_time = int(time*2.2)
        adb.touch(x1,y1,cal_time)
        




if __name__ == "__main__":
    adb = Adb()
    jmp = jumpmaster()
    while True: 
        img = adb.screenshot()
        canvas = np.copy(img)  
        try:
            canvas,che_x,che_y = jmp.findChess(img,canvas)
        except TypeError :
            continue
        
        cv.imshow("liang.png",canvas)
        cv.setMouseCallback("liang.png",mouse_val)
        cv.waitKey(800)
        

        
            
    cv.destroyAllWindows()

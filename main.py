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
        time = math.sqrt(abs(che_x - x)**2 + abs(che_y - y)**2)
        print("distance : ",math.sqrt(abs(che_x - x)**2 + abs(che_y - y)**2))
        cal_time = int(time*2.5)
        adb.touch(cal_time)




if __name__ == "__main__":
    
    adb = Adb()
    jmp = jumpmaster()
    while True: 
        img = adb.screenshot()
        canvas = np.copy(img)  
        canvas,che_x,che_y = jmp.findChess(img,canvas)
        cv.imshow("liang.png",canvas)
        cv.setMouseCallback("liang.png",mouse_val)
        cv.waitKey(500)

        
            
    cv.destroyAllWindows()

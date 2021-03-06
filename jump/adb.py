'''
author : liangwei

'''
import subprocess as sub 
import shlex 
import cv2 as cv 
import numpy as np 
import math


class Adb:

    def __init__(self):
        self.img = None

    def screenshot(self):
        ''' get an image from android phone'''
        sub.call("adb shell screencap -p | sed 's/\r$//' > liang.png",shell = True)
        img = cv.imread("liang.png",1)
        cv.imshow("img",img)
        resize = cv.resize(img,(700,900))
        self.img = resize
        return self.img

    def againtencent(self):
        pass

    def touch(self,che_x,che_y,x,y):
        x1 = np.random.randint(550,600)
        y1 = np.random.randint(350,550)
        time = math.sqrt(abs(che_x - y)**2 + abs(che_y - (x+40))**2)
        print(time)
        cal_time = int(time*2.2)
        sub.call("adb shell input touchscreen swipe {} {} {} {} {}".format(x1,y1,x1+20,y1+20,cal_time),shell = True)



if __name__ == "__main__":
    adb = Adb()
    adb.screenshot()
    adb.againtencent()
    cv.waitKey(0)
    cv.destroyAllWindows()

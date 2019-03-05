import subprocess as sub 
from subprocess import Popen,PIPE
import shlex 
import cv2 as cv 
import numpy as np 
import os

cmd = " "
lis = []    
#p = Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE, stderr=PIPE)
a = 0
while True:
    
   
    sub.call("adb shell screencap -p | sed 's/\r$//' > liang.png",shell = True)

    img = cv.imread("liang.png",-1)
    resize = cv.resize(img,(700,900))
    cv.imshow("liang.png",resize)
    key_num = cv.waitKey(0)
    
    a +=1
    if key_num == ord("s"):
        cv.imwrite("train/{}.png".format(a),resize)
    if key_num == ord('c'):
        continue 

    if key_num == ord('q'):
        break
        
    if key_num == ord("j"):
        sub.call("adb shell input touchscreen swipe 400 400 400 400 750 " ,shell = True)

    if key_num == ord('d'):
        del_command = "ls train/"
        p = sub.Popen(shlex.split(del_command),stdin= PIPE,stdout= PIPE)
        out, err = p.communicate()
            


            
cv.destroyAllWindows()
    
   
    













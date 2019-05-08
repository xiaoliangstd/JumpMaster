# -*- coding: utf-8 -*- 
from FGJumperMaster import FGJumperMaster
from ADBHelper import ADBHelper
from FGVisonUtil import FGVisionUtil as vutil
import cv2
import numpy as np
import time
import datetime

# 初次读入图片
img = ADBHelper.getScreenShotByADB()
vutil.printImgInfo(img)

adb = ADBHelper(1080, 1920)

cv2.namedWindow('image', flags= cv2.WINDOW_NORMAL | cv2.WINDOW_FREERATIO)

keyPressed = -1


def distance2time(distance):
    ratio = 1.53
    # 事件必须是整数类型
    return int(distance * ratio)


def saveSampleImg(jmaster, img, tag=True):
    img_name = f"{datetime.datetime.now():%Y-%m-%d-%H-%M-%S.png}"
    
    if tag:
        cv2.imwrite("./samples/right/"+img_name, img)
        cv2.imwrite("./samples/right_log/"+img_name, jmaster.visualization_detail())
    else:
        cv2.imwrite("./samples/wrong/"+img_name, img)
        cv2.imwrite("./samples/wrong_log/"+img_name, jmaster.visualization_detail())

markflag = 0
chessPtr = (0, 0)
boxPtr = (0, 0)
isMarked = False

'''
手动标注

'''
def markChessAndBoxByHand(event,x,y,flags,param):
    global markflag
    global chessPtr
    global boxPtr
    global isMarked
    global subImg

    if event == cv2.EVENT_LBUTTONDOWN:
        
        if markflag == 0 and isMarked == False:
            # 开始标注chess
            # 更新chess的坐标
            
            chessPtr = (x, y)
            print("已标注 chess坐标 {}, {}".format(chessPtr[0], chessPtr[1]))
            cv2.circle(subImg,(x,y), int(5), (0, 0, 255), -1)
            markflag = 1
        elif markflag == 1 and isMarked == False:
            boxPtr = (x, y)
            print("已标注 box中心坐标 {}, {}".format(boxPtr[0], boxPtr[1]))
            cv2.circle(subImg,(x,y), int(5), (255, 0, 0), -1)
            markflag = 2

    elif event == cv2.EVENT_LBUTTONUP and markflag == 2:
        # 检测到鼠标左键抬起
        isMarked = True
        markflag = 0
    # 更新图片
    cv2.imshow("image", subImg)


# 设置鼠标事件回调
cv2.setMouseCallback('image',markChessAndBoxByHand)  

subImg = None
while True:
    img = ADBHelper.getScreenShotByADB()
    
    subImg = img[300:1720, :]
    
    try:
        jmaster = FGJumperMaster(subImg)
        # 预览算法效果与过程
        subImg = jmaster.visualization()
        cv2.imshow("image",jmaster.visualization())
    except IndexError:

        cv2.imshow("image", subImg)
    

    keyPressed = cv2.waitKey(0)
    if keyPressed == ord("e"):
        print("游戏结束")
        break
    elif keyPressed == ord("y"):
        
        if isMarked:
            saveSampleImg(jmaster, img, tag=False)
            isMarked = False
            markflag = 0
            distance = vutil.cal_distance(chessPtr, boxPtr)
            print("手动distance %.2f"%distance)
            delay = distance2time(distance)
            rc = ADBHelper.pressOnScreen((500, 500), delay=delay)
            if rc:
                print("成功点击 并延时 1s")
                time.sleep(0.5 + delay / 1000)

            continue
        # 识别正确，确认点击
        delay = distance2time(jmaster.distance)
        rc = ADBHelper.pressOnScreen((500, 500), delay=delay)
        saveSampleImg(jmaster, img)
        if rc:
            print("成功点击 并延时 1s")
            time.sleep(0.5 + delay / 1000)

    elif keyPressed == ord("n"):
        # 保存失败样例及日志
        saveSampleImg(jmaster, img, tag=False)

    isMarked = False
    markflag = 0
cv2.destroyAllWindows()
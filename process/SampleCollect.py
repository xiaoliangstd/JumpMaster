# -*- coding: utf-8 -*- 
'''
获取部分测试样例
存放在./samples文件夹下.

'''

import numpy as np
import cv2
# 如果你选了多个摄像头的话， 需要设定VideoCapture序号， 1 or 0  or else。
# 0 : camera on my laptop
# 1 : usb camera
cap = cv2.VideoCapture(1)

# 这里可以设置画面的宽度跟高度
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
# 图像采集计数
img_count = 1

while(True):
    # Capture frame-by-frame
    # 逐帧获取画面
    # ret 画面是否获取成功
    # 	True 获取成功
    # 	False 获取失败
    ret, frame = cap.read()
    
    # 转变为灰度图
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 展示图片
    # 这里的'frame' 指代的是窗口名称为fram
    #cv2.imshow('frame', frame)
	# 镜像翻转， 你可能不需要
    cv2.flip(frame, -1)
    # 获取图片的行数 列数， 与通道数
    (rows,cols,channels) = frame.shape
	
    # 这里我旋转了一下图像， 因为我采集过来是横着的，所以需要旋转90度
    M = cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
    dst = cv2.warpAffine(frame, M, (cols,rows))
	# 显示最终画面。
    cv2.imshow('frame', dst)
	# 等待按键按下， 最多等待1ms
    key = cv2.waitKey(1)
	# 如果按键等于q （小写q）
    if key == ord('q'):
        # 退出程序
        break
    elif key == ord('c'):
        # 如果按键是c 说明需要捕捉画面
        cv2.imwrite("{}.png".format(img_count), dst)
        # 画面计数+1
        img_count += 1

# 程序退出的时候
# 释放VideoCapture
cap.release()
# 关闭所有窗口
cv2.destroyAllWindows()

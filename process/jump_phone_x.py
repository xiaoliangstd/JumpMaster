# coding: utf-8
import os
import sys
import subprocess
import shutil
import time
import math
from PIL import Image, ImageDraw
import random
import json
import re

import cv2
import numpy as np
from scipy import ndimage
import serial
import struct
import os


def rotateImage(image, angle):
    img_size=image.shape
    img_c=img_size[2]
    img_w=img_size[1]
    img_h=img_size[0]
    img_max_size=max(img_w,img_h)
    des_img=np.zeros((img_max_size,img_max_size,img_c),dtype=np.uint8)
    if img_h==img_max_size:
        des_img[:,int((img_max_size-img_w)/2):int((img_max_size-img_w)/2)+img_w]=image.copy()
    else:
        des_img[int((img_max_size-img_h)/2):int((img_max_size-img_h)/2)+img_h,:]=image.copy()
    image_center = (img_max_size/2,img_max_size/2)
    rot_mat = cv2.getRotationMatrix2D(image_center,angle,1)
    result = cv2.warpAffine(des_img, rot_mat, (img_max_size,img_max_size),flags=cv2.INTER_LINEAR)
    if img_h==img_max_size:
        result_crop=result[int((img_max_size-img_w)/2):int((img_max_size-img_w)/2)+img_w,:]
    else:
        result_crop=result[:,int((img_max_size-img_h)/2):int((img_max_size-img_h)/2)+img_h]
    return result_crop


def open_op(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3, 3))
    opened_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return opened_mask

def open_op_large(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(8, 8))
    opened_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return opened_mask

def open_op_mid(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5, 5))
    opened_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return opened_mask

def close_op(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3, 3))
    closed_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return closed_mask

def dila_op(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3, 6))
    closed_mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
    return closed_mask

def close_op_large(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(6, 12))
    closed_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return closed_mask


#detect the jump body
#color
def self_detect(img):
    region_upper=int(img.shape[0]*0.3)
    region_lower=int(img.shape[0]*0.7)
    region=img[region_upper:region_lower]

    hsv_img=cv2.cvtColor(region,cv2.COLOR_BGR2HSV)
    color_lower=np.int32([105,25,45])
    color_upper=np.int32([135,125,130])

    color_mask = cv2.inRange(hsv_img, color_lower, color_upper)

    color_mask = open_op(color_mask)
    color_mask = close_op_large(color_mask)
    #cv2.imshow('color_mask_self',color_mask)

    contours= cv2.findContours(color_mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[1]
    if len(contours)>0:
        max_contour = max(contours, key=cv2.contourArea)
        max_contour = cv2.convexHull(max_contour)

        rect = cv2.boundingRect(max_contour)
        x,y,w,h = rect

        center_coord=(x+w/2,y+h+region_upper - 10)
        cv2.circle(img, center_coord, 5, (0,255,0), -1)

        return center_coord


#goal block detect
def goal_detect(img,body_position):
    region_upper=int(img.shape[0]*0.3)
    region_lower=int(img.shape[0]*0.6)

    if body_position[0]<(img.shape[1]/2.0):
        region_left=body_position[0]+15
        region_right=img.shape[1]
    else:
        region_left=0
        region_right=body_position[0]-15

    region = img[region_upper:region_lower, region_left:region_right]

    edge_region_list=[]
    for idx in xrange(3):
        region_gray=cv2.cvtColor(region,cv2.COLOR_BGR2HSV)[:,:,idx]
        region_shape=region.shape
        region_gray=cv2.GaussianBlur(region_gray,(5,5),0)
        region_sobel = np.abs(cv2.Sobel(region_gray,cv2.CV_32F,0,1,ksize=3))
        cv2.imshow('region_sobel', region_sobel)
        region_sobel = np.uint8(region_sobel)
        region_sobel=cv2.threshold(region_sobel,15,255,cv2.THRESH_BINARY)[1]
        region_sobel=open_op(region_sobel)
        region_sobel=close_op_large(region_sobel)
        region_sobel=np.uint8(region_sobel)
        edge_region_list.append(region_sobel)

    region_sobel_final=np.bitwise_or(edge_region_list[0],edge_region_list[1])
    region_sobel_final=np.bitwise_or(region_sobel_final,edge_region_list[2])
    #cv2.imshow('region',region_sobel_final)
    contours= cv2.findContours(region_sobel_final,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[1]

    if len(contours)>0:
        contours_all=np.empty((0,1,2))
        for cnt in contours:
            if cv2.contourArea(cnt)>50:
                contours_all=np.concatenate((contours_all,cnt),axis=0)

        most_up_args=np.argmin(contours_all[:,0,1])
        most_up_point_sum=np.float32([0,0])
        most_up_point_sum[0]=contours_all[most_up_args,0,0]
        most_up_point_sum[1]=contours_all[most_up_args,0,1]
        most_up_point=most_up_point_sum

        most_up_point[1]+=35
        most_up_point[0]+=region_left
        most_up_point[1]+=region_upper
        cv2.circle(img, (int(most_up_point[0]),int(most_up_point[1])), 5, (0,0,255), -1)
        return most_up_point

def cal_dis(center1,center2):

    dis_x=abs(center1[0]-center2[0])
    dis_y=abs(center1[1]-center2[1])
    dis=np.sqrt(pow(dis_x,2)+pow(dis_y,2))
    return dis


def check_adb():
    flag = os.system('adb devices')
    if flag == 1:
        print('请安装ADB并配置环境变量')
        sys.exit()

idx = 0
def pull_screenshot():
    process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
    screenshot = process.stdout.read()
    if sys.platform == 'win32':
        screenshot = screenshot.replace(b'\r\n', b'\n')
    f = open('autojump.png', 'wb')
    f.write(screenshot)
    f.close()
    global idx
    f = open('test_imgs/img_%d.png'%(idx), 'wb')
    f.write(screenshot)
    f.close()
    idx +=1

def serial_send(Serial,dis):
    send_str=struct.pack('<ccfcc','a','5',dis,'f','f')
    print repr(send_str)
    Serial.write(send_str)


def jump(distance):
    press_time = distance * 4.3             #此处参数还需要仔细调整
    press_time = max(press_time, 200)  # 设置 200 ms 是最小的按压时间
    press_time = int(press_time)
    print(press_time)
    serial_send(ser, press_time)
    time.sleep(press_time / 1000.0)

#prepare the serial port
ser = serial.Serial('/dev/ttyUSB0',115200)
print ser.portstr

while True:
    pull_screenshot()

    frame = cv2.imread('./autojump.png')

    #frame=rotateImage(frame,90)
    frame=cv2.resize(frame,(720,1280))
    body_coord=self_detect(frame)

    if body_coord is not None:
        print 'body position:',body_coord

        goal_coord = goal_detect(frame,body_coord)
        cv2.imshow('frame', frame)

        dis_norm = abs(goal_coord[0] - body_coord[0])

        #dis_norm = math.sqrt(goal2body_coord[0]*goal2body_coord[0] + goal2body_coord[1]*goal2body_coord[1])

        jump(dis_norm)
        time.sleep(random.uniform(1.5, 2))

        cv2.waitKey(10)

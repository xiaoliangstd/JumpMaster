# -*- coding: utf-8 -*- 
import cv2
import numpy as np

import matplotlib.pyplot as plt
import math
import random

class FGVisionUtil:
    '''
        凡哥的机器视觉工具箱

    '''


    @staticmethod
    def cal_rgb_margin(img):
        '''
            计算采样色块区域RGB 三通道的阈值
        '''
        # 计算色块的 

        (minB, maxB) = FGVisionUtil.cal_single_margin(img, 0)
        (minG, maxG) = FGVisionUtil.cal_single_margin(img, 1)
        (minR, maxR) = FGVisionUtil.cal_single_margin(img, 2)

        threshold_lower = np.int32([minB, minG, minR])
        threshold_upper = np.int32([maxB, maxG, maxR])
        
        return (threshold_lower, threshold_upper)
    
    @staticmethod
    def cal_single_margin(img, channel):
        '''
            计算采样色块区域单个通道的阈值边界
        '''
        # 柱形统计
        hist = cv2.calcHist([img], [channel], None, [256], [0, 256])
        hist = hist.reshape((len(hist)))
        # 概率分布
        prob =  hist / hist.sum()
        # 计算颜色累计分布
        prob_accum = np.zeros_like(prob)
        prob_accum[0] = prob[0]


        # 阈值下界确定状态
        lower_status = False
        # 阈值上界确定状态
        upper_status = False

        # 概率累计分布最小值

        lower_prob = 0.05
        # 概率累计分布最大值

        upper_prob = 0.95

        # 阈值下界值
        lower_value = 0
        # 阈值上界值
        upper_value = 0

        for i in range(1, len(prob)):
            prob_accum[i] = prob[i] + prob_accum[i-1]
            
            # 确定阈值下界
            if not lower_status and prob_accum[i] > lower_prob:
                lower_value = i
                lower_status = True
            # 确定阈值上界
            if not upper_status and prob_accum[i] > upper_prob:
                upper_value = i
                upper_status = True


        return (lower_value, upper_value)
    
    @staticmethod
    def draw_gray_hist(img):
        '''
            绘制灰度图的直方图
        '''
        # 样例图片
        plt.hist(img.ravel(), bins=256, range=[0, 256])
        plt.show()

    @staticmethod
    def draw_rgb_hist(img):
        '''
            绘制RGB彩图的直方图
        '''
        # 获取顶部长条(只有背景图片)
        color = ('b', 'g', 'r')  
        for i, col in enumerate(color): 
            histr = cv2.calcHist([img], [i], None, [256], [0, 256])
            plt.plot(histr, color=col)  
        plt.xlim([0, 256])  
        plt.show()  

    @staticmethod
    def justify_rgb_value(color):
        '''
            根据RGB的取值范围重新调整 RGB的值
        '''
        MIN_RGB_VALUE = 0
        MAX_RGB_VALUE = 255
        
        ncolor = np.copy(color)
        for channel in range(3):
            if ncolor[channel] < MIN_RGB_VALUE:
                ncolor[channel] = MIN_RGB_VALUE
            elif ncolor[channel] > MAX_RGB_VALUE:
                ncolor[channel] = MAX_RGB_VALUE
        return ncolor
    
    @staticmethod
    def contours_filter(contours, minWidth=None, maxWidth=None, minHeight=None, maxHeight=None, minArea=None):
        '''
            contours筛选器
        '''    
        newCntList = []

        for cnt in contours:
            
            rect = cv2.minAreaRect(cnt)       # 获取最小矩形区域
            area = cv2.contourArea(cnt)       # 获取contour的面积

            width = rect[1][0]
            height = rect[1][1]

            if minWidth and width < minWidth:
                continue
            if maxWidth and width > maxWidth:
                continue
            if minHeight and height < minHeight:
                continue
            if maxHeight and height > maxHeight:
                continue
            if minArea and area < minArea:
                continue

            newCntList.append(cnt)
        return newCntList            
    
    
    @staticmethod
    def isPointInRectangle(rect, pt):
        (px, py) = pt
        (x, y, w, h) = rect

        if px < x or px > x + w:
            return False
        elif py < y or px > y + h:
            return False

        return True
    
    @staticmethod
    def printImgInfo(img):
        print("================打印一下图像的属性================")
        print("图像对象的类型 {}".format(type(img)))
        print(img.shape)
        print("图像宽度: {} pixels".format(img.shape[1]))
        print("图像高度: {} pixels".format(img.shape[0]))
        print("通道: {}".format(img.shape[2]))
        print("图像分辨率: {}".format(img.size))
        print("数据类型: {}".format(img.dtype))
    
    @staticmethod
    def cal_distance(pt1, pt2):
        '''
            获取棋子与下一跳盒子的距离
        '''
        (x1, y1) = pt1
        (x2, y2) = pt2

        return math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))
    
    @staticmethod
    def fitBGRBValue(rgb_value, addWeight=0):
        '''
            rgb值 添加或者减去一个值，并确保数值范围在合理区间内 0 - 255
        '''
        MIN_VALUE = 0
        MAX_VALUE = 255
        for i in range(len(rgb_value)):
            if rgb_value[i] + addWeight < MIN_VALUE:
                rgb_value[i] = MIN_VALUE
            elif rgb_value[i] + addWeight > MAX_VALUE:
                rgb_value[i] = MAX_VALUE
            else:
                rgb_value[i] += addWeight
        return rgb_value
    
    @staticmethod
    def findCurveBoundary(array, start, win_size=1, zero_threshold=0, offset=(0,0)):
        '''
            给定一个切入点， 获取该点所在颜色分布
        '''
        bin_num = len(array)
        leftb = start
        rightb = start
        while leftb >= 0 and array[leftb] > zero_threshold:
            leftb -= 1
        
        while rightb < bin_num and array[rightb] > zero_threshold:
            rightb += 1

        return (max(0, leftb*win_size+offset[0]), min(255, rightb*win_size+offset[1]))
    
    @staticmethod
    def getMaxCurveBoundary(array, win_size=4,zero_threshold=0, offset=(0,0)):
        '''
            找到背景色的边界， 默认占比最大的颜色分布为背景色的颜色分布
        '''
        segments = []
        bin_num = len(array)

        binIdx = 0
        while binIdx < bin_num:
            if array[binIdx] < zero_threshold:
                #print('next %d'%(binIdx))
                pass
            else:
                # 找到一个区域
                segment = [binIdx, binIdx, array[binIdx]]
                binIdx += 1
                while binIdx < bin_num and array[binIdx] > zero_threshold:
                    segment[1] = binIdx
                    segment[2] += array[binIdx]
                    binIdx += 1
                segments.append(segment)           
            binIdx += 1
        
        # 从segments列表中寻找面积最大的（segment[2]）
        max_segment = max(segments, key=lambda s:s[2])
        return (max(0,max_segment[0]*win_size+offset[0]), min(255,max_segment[1]*win_size+offset[1]))

    @staticmethod
    def generateRandomColor():
        return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

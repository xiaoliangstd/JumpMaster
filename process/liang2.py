# -*- coding: utf-8 -*- 
import math
import cv2
import numpy as np
from FGVisonUtil import FGVisionUtil as vutils


class liangmaster():
    '''
        凡哥的 < 跳一跳 > 游戏大师
        ---------------------------------------
        功能列表
            * 去除背景与阴影部分
            * 获取棋子的位置
            * 获取下一跳盒子的中心点的位置
            * 计算棋子与下一跳盒子的距离

    '''
    def __init__(self, img):
        # 采集的图像
        self.img = img
        self.img_nobg = None # 去除背景与阴影的图片

        # 背景图片
        self.bg_lcolor = None # 背景颜色阈值下界  background color lower
        self.bg_ucolor = None # 背景颜色阈值上界  background color upper 
        self.bg_mask = None # 背景的罩层 background mask
        
        # 阴影部分
        self.shd_lcolor = None # 盒子阴影颜色阈值下界 shadow color lower
        self.shd_ucolor = None # 盒子阴影颜色阈值上界 shadow color upper
        self.shd_mask = None # 盒子阴影罩层 shadow mask
        
        # 棋子 (画面中的小人)
        self.chs_lcolor = np.int32([105, 25, 45]) # 棋子的颜色阈值下界 chess color lower
        self.chs_ucolor = np.int32([135 ,125 ,130]) # 棋子的颜色阈值上界 chess color upper
        self.chs_mask = None # 棋子的罩层
        self.chs_rect = None # 棋子所在的矩形区域
        self.chs_fposi = None # 棋子底部中心的位置 chess foot position
        
        # 盒子
        self.box_max_width = 125
        self.box_max_height = 125 # 盒子的最大高度
        self.box_mask = None # 盒子的罩层
        self.nbox_contour = None # 
        self.nbox_rect = None # 下一跳盒子的位置
        self.nbox_center = None # 下一跳盒子顶部的中心
        self.distance = None
        self.box_inver = None

        # 计算图像背景罩层
        self.cal_background_mask()
        # 获取阴影部分的罩层
        self.cal_shadow_mask()
        # 获取盒子的罩层
        self.cal_box_mask()
        # 将盒子的罩层与原图像进行运算, 获取不带背景与阴影的图片
        self.make_img_without_bg()
        # 计算棋子的罩层, 颜色阈值是提前设定好的. 
        self.cal_chs_mask()
        # 计算棋子底部的位置
        self.cal_chess_foot_posi()
        # 获取最顶层盒子的中心
        self.cal_top_box_center()
        # 获取棋子与下一跳盒子的距离
        self.cal_distance()
        

    def cal_background_mask(self):
        '''
            计算图像背景罩层
        '''

        # 采集图像顶部 高度为100像素点的区域,对背景颜色进行统计
        # 你也可以根据你的画面自行修改

        bg_sample = self.img[200:400, 0:200] 
                                    
        # 分析背景样本图片, 得到背景颜色的阈值
        (self.bg_lcolor, self.bg_ucolor) = vutils.cal_rgb_margin(bg_sample)

        # 因为摄像头采集的时候, 光照分布, 导致图片不同区域的背景颜色差异.
        # 背景色以顶部为准, 并适当放大一下背景色的取值范围, 我们这里取20
        self.bg_lcolor = vutils.justify_rgb_value(self.bg_lcolor - 20)
        self.bg_ucolor = vutils.justify_rgb_value(self.bg_ucolor + 20)
        # 获取背景罩层
        self.bg_mask = cv2.inRange(self.img, self.bg_lcolor, self.bg_ucolor)
        # 对背景罩层进行处理 数学形态学运算, 去除噪声
        # 用7*7 的核对背景图片进行闭运算
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(7, 7))
        self.bg_mask = cv2.morphologyEx(self.bg_mask, cv2.MORPH_CLOSE, kernel)  

    def cal_shadow_mask(self):
        '''
            获取阴影部分的罩层
        '''
        # 根据颜色的统计分布 阴影部分的颜色取值 
        # 实际是背景颜色的平移, 所以我们在背景色的阈值上, 左移
        self.shd_lcolor = vutils.justify_rgb_value(self.bg_lcolor - 60)
        self.shd_ucolor = vutils.justify_rgb_value(self.bg_ucolor - 50)
        # 获取阴影的罩层
        self.shd_mask = cv2.inRange(self.img, self.shd_lcolor, self.shd_ucolor)
        # 对获取的阴影罩层进行数学形态运算, 去除噪声
        # 使用 9*9的核进行闭运算
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(9, 9))  
        # open close
        self.shd_mask = cv2.morphologyEx(self.shd_mask, cv2.MORPH_OPEN, kernel)  
    
    def cal_box_mask(self):
        '''
            获取盒子的罩层
            盒子的罩层在背景罩层与阴影罩层的 二进制运算的基础上求得
        '''
        self.box_inver = cv2.bitwise_or(self.bg_mask, self.shd_mask)
        self.box_mask = cv2.bitwise_not(cv2.bitwise_or(self.bg_mask, self.shd_mask))
        # 闭运算 去除噪声
        k1 = cv2.getStructuringElement(cv2.MORPH_RECT,(6, 6)) 
        self.box_mask = cv2.morphologyEx(self.box_mask, cv2.MORPH_CLOSE, k1) 
    

    
    def make_img_without_bg(self):
        '''
            将盒子的罩层与原图像进行运算, 获取不带背景与阴影的图片
        '''
        self.img_nobg = cv2.bitwise_and(self.img, self.img, mask=self.box_mask)
        
    def cal_chs_mask(self):
        '''
           计算棋子的罩层, 颜色阈值是提前设定好的. 
        '''
        hsv_img = cv2.cvtColor(self.img,cv2.COLOR_BGR2HSV)
        self.chs_mask = cv2.inRange(hsv_img, self.chs_lcolor, self.chs_ucolor)

       
        #开运算 clean the noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(8, 8)) 
        self.chs_mask = cv2.morphologyEx(self.chs_mask, cv2.MORPH_OPEN, kernel)

         #闭运算   make  liantong 
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(8, 8))  
        self.chs_mask = cv2.morphologyEx(self.chs_mask, cv2.MORPH_CLOSE, kernel)  
 

    def cal_chess_foot_posi(self):
        '''
            计算棋子底部的位置
        '''
        # 寻找当前棋子所处的矩形区域 (联通域)
        (x,y,w,h) = cv2.boundingRect(self.chs_mask)
        # 记录棋子所在的矩形区域
        self.chs_rect = (x, y, w, h)
        self.chs_fposi = (int(x+w/2), y+h)

    def cal_top_box_center(self):
        '''
            获取最顶层盒子的中心
        '''

        canvas = np.copy(self.img)

        image, contours, hier = cv2.findContours(self.box_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        contours = vutils.contours_filter(contours, minHeight=50, minWidth=50)
        
        boxes = []

        
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            boxes.append((x, y, w, h))

        top_box = boxes[0]
        top_contour = contours[0]

        for i in range(1, len(contours)):
            # 对比box的y坐标的值, 获取最小 也就是最靠上方的盒子
            box = boxes[i]
            if top_box[1] > box[1]:
                top_box = box
                top_contour = contours[i]

        # print("box : {}".format(top_box))

        (x, y, w, h) = top_box
        
        # 这里有个问题， 如果两个box离的很近
        # 当前的盒子跟下一跳的盒子的区域会联通， 所以需要裁减
        # 通过判断chess是否在box中， 来判断是否相邻的两个盒子被当成一个。
        if vutils.isPointInRectangle(top_box, self.chs_fposi):
            # 检测到盒子连体， 采用备用方案， 获取下一个盒子的中心。
            
            miny = 100000
            ptop = None
            for points in top_contour:
                (px, py) = points[0]
                if py < miny:
                    miny = py
                    ptop = (px, py)
            # 把最顶上的坐标中x点作为box中心点。
            cx = ptop[0]
            dh =  int(abs(cx - self.chs_fposi[0]) / math.sqrt(3))
            cy = self.chs_fposi[1] - dh
            
            radius = abs(cy - ptop[1])

            (x, y, w, h) = (cx - radius, ptop[1], 2*radius, 2*radius)
            
            # 再次判断chess底部是否落在矩形区域内
            # 进行对应的放缩
            # 下面的这段代码纯属靠凡哥发挥 实验有效。
            if vutils.isPointInRectangle((x, y, w, h), self.chs_fposi):
                # 这里移动值， 我选的是chess矩形区域的宽度
                delta = self.chs_rect[2]
                if self.chs_fposi[0] < x:
                    x -= delta
                else:
                    x += delta
                w -= delta
                h -= delta
            self.nbox_rect = (x, y, w, h)
            
            # 重新调整中心
            self.nbox_center = (int(x + w / 2), int(y + h / 3))

        else:
            self.nbox_rect = (x, y, w, h)
            (x, y, w, h) = self.nbox_rect
            # 计算中心点, 立体盒子的高的1/3处大概就是中心点y坐标的位置
            # 中心点的x左边标定为宽度的1/2处.
            self.nbox_center = (int(x + w / 2), int(y + h / 3))
        (x22,y22,w22,h22) = self.nbox_rect
        x33,y33 = self.chs_fposi
        x44,y44 = self.nbox_center
        cv2.rectangle(canvas,(x22,y22),(x22+w22,y22+h22),(255,0,0),5)
        cv2.circle(canvas,(x33,y33),5,(0,0,255),-1)
        cv2.circle(canvas,(x44,y44),5,(0,0,255),-1)
        cv2.imshow('canvas',canvas)

    def cal_distance(self):
        '''
            获取棋子与下一跳盒子的距离
        '''
        (x1, y1) = self.chs_fposi
        (x2, y2) = self.nbox_center

        self.distance = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))
    
    def cal_delay(self):
        ratio = 1.53
        # 事件必须是整数类型
        return int(self.distance * ratio)

    def visualization(self):
        '''
            可视化 计算过程.
        '''
        
        # 选择字体
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.5
        # 创建画布
        canvas = np.copy(self.img)
        
        # 绘制棋子所在的矩形
        (x, y, w, h) = self.chs_rect
        cv2.rectangle(img=canvas, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 0), thickness=2)
        # 绘制棋子底部的中心点 红色实心
        cv2.circle(img=canvas, center=self.chs_fposi, radius=5, color=(0, 0, 255), thickness=-1)
        # 标注棋子坐标
        (x, y) = self.chs_fposi
        cv2.putText(canvas, text='(x={},y={})'.format(x, y), org=(x-40, y+20), fontFace=font, fontScale=fontScale, thickness=1, 
            lineType=cv2.LINE_AA, color=(0, 0, 255))

        # 绘制最顶部的盒子
        (x, y, w, h) = self.nbox_rect
        cv2.rectangle(img=canvas, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
        # 绘制盒子顶部的中心点
        cv2.circle(img=canvas, center=self.nbox_center, radius=5, color=(0, 0, 255), thickness=-1)
        cv2.putText(canvas, text='W={},H={}'.format(w, h), org=(20, 40), fontFace=font, fontScale=fontScale, thickness=1, 
            lineType=cv2.LINE_AA, color=(0, 0, 255))

        # 标注盒子中心点坐标
        (x, y) = self.nbox_center
        cv2.putText(canvas, text='(x={},y={})'.format(x, y), org=(x-20, y-20), fontFace=font, fontScale=fontScale, thickness=1, 
            lineType=cv2.LINE_AA, color=(0, 0, 255))
        

        # 在棋子跟盒子中心点之间绘制一条直线
        cv2.line(canvas, pt1=self.chs_fposi, pt2=self.nbox_center, color=(0, 0, 255))
        # 标注距离
        cv2.putText(canvas, text='DIS: %.3f'%(self.distance), org=(20, 20), fontFace=font, fontScale=fontScale, thickness=1, 
            lineType=cv2.LINE_AA, color=(0, 0, 255))

        return canvas


    def visualization_detail(self):
        '''
            展示计算过程中的流程, 方便排错

            需要统一颜色通道, 才能将其合并 作为一幅图片展示
        '''

        output = self.visualization()
        bg_mask = cv2.cvtColor(self.bg_mask, cv2.COLOR_GRAY2BGR)
        shd_mask = cv2.cvtColor(self.shd_mask, cv2.COLOR_GRAY2BGR)
        box_mask = cv2.cvtColor(self.box_mask, cv2.COLOR_GRAY2BGR)
        chs_mask = cv2.cvtColor(self.chs_mask, cv2.COLOR_GRAY2BGR)
        return np.hstack((output, bg_mask, shd_mask, box_mask, self.img_nobg, chs_mask))


if __name__ == '__main__':
    
    
    img = cv2.imread('53.png',-1)
    liang = liangmaster(img)
    liang.cal_chs_mask()
    liang.cal_background_mask()
    liang.cal_box_mask()
    liang.cal_top_box_center()
    liang.make_img_without_bg()
    liang.cal_chess_foot_posi()
    liang.cal_top_box_center
    liang.cal_shadow_mask()
        #c = liang.cal_distance()
        #cv2.imshow('distance',c)
    cv2.imshow('box_mask',liang.box_mask)
    cv2.imshow('bg_mask',liang.bg_mask)
    cv2.imshow('sd_mask',liang.shd_mask)
    cv2.imshow('chess_mask',liang.chs_mask)
    
        #cv2.imshow('chess_mask',liang.chs_mask)
        #cv2.imshow('img_nobg',liang.img_nobg)
        

    
    cv2.waitKey(0)
    
    cv2.destroyAllWindows()
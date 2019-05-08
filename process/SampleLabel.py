'''
程序说明:
    程序类用于通过鼠标手动标注两个关键点坐标
    1. 棋子中心
    2. 下一跳盒子的中心
'''

import cv2
import numpy as np
import datetime
import math
import copy
from ADBHelper import ADBHelper

# MP : Mark Process 标注过程
MP_UNMARK = 0 # 0 : 未进行标注
MP_MARKED_FCHESS = 1  # 1 : 标注了小人的底部
MP_MARKED_CBOX = 2 # 2 : 标注了box的中心点

'''
手动标注 两个标签

'''
def markChessAndBoxByHand(event,x,y,flags,sampleLabel):
    
    if event == cv2.EVENT_LBUTTONDOWN:
        print("click: x= {}, y={}".format(x, y))
        sampleLabel.addLabel(x, y)
    

class SampleLabel:
    def __init__(self, save_path='./', label_filename='label.txt'):
        self.img = None # 原来的图片
        self.canvas = None # 画布
        self.img_name = None # 图片名称
        self.mp = 0 # 标注的进程 mark process
        self.fchess = (0, 0) # 棋子底部中心
        self.cbox = (0, 0) # 下一条盒子的中心
        self.save_path = save_path # 图像的保存路径
        self.label_filename = label_filename #　标签记录文件的文件名
        # self.label_file = open(label_filename, 'w+') # 文件对象
        self.winname = 'label'
        
        # 创建一个窗口
        cv2.namedWindow(self.winname, flags= cv2.WINDOW_NORMAL | cv2.WINDOW_FREERATIO)
        # 设置鼠标事件的回调函数
        cv2.setMouseCallback(self.winname, markChessAndBoxByHand, self)


    def updateImg(self, img, img_name = None):
        # 更新当前源图像 - 深度拷贝
        self.img = img.copy()
        # 更新画布 - 深度拷贝
        self.canvas = img.copy()
        # 重置 棋子底部坐标
        self.fchess = (0, 0)
        # 重置盒子的中心
        self.cbox = (0, 0)

        if img_name == None:
            # 根据时间戳　生成文件名
            self.img_name = f"{datetime.datetime.now():%Y-%m-%d-%H-%M-%S-%f.png}"
        else:
            # 如果有名字的话就直接赋值
            self.img_name = img_name

        # 重置标注状态
        self.mp = MP_UNMARK
        # 更新画布
        self.updateCanvas()

    def printProcessOnCanvas(self, info):
        '''
            在画布上显示帮助信息
        '''
        # 首先更新画布
        # self.updateCanvas()
        self.canvas[50:150,:] = 255
        # 选择字体
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        cv2.putText(self.canvas, text=info, org=(100, 100), fontFace=font, fontScale=fontScale, thickness=1, 
                     lineType=cv2.LINE_AA, color=(0, 0, 255))
        

        cv2.imshow(self.winname, self.canvas)

    def updateCanvas(self):
        '''
            根据状态更新画布　与文字提示
        '''
        # Use Deep Copy
        self.canvas = self.img.copy()

        rmarker = 10 # 标记半径
        if self.mp >= MP_MARKED_FCHESS:
            # 绘制chess中心
            # 绘制棋子底部的中心点 红色实心
            cv2.circle(img=self.canvas, center=self.fchess, radius=rmarker, color=(0, 0, 255), thickness=-1)
            
        if self.mp >= MP_MARKED_CBOX:
            # 绘制下一条盒子中心
            cv2.circle(img=self.canvas, center=self.cbox, radius=rmarker, color=(0, 255, 0), thickness=-1)

        if self.mp == MP_UNMARK:
            self.printProcessOnCanvas("step-0 unmarked, mark chess footer first.")

        elif self.mp == MP_MARKED_FCHESS:
            self.printProcessOnCanvas("step-1  you need to mark next box center.") 
    
        elif self.mp == MP_MARKED_CBOX:
            self.printProcessOnCanvas("step-2 mark done, save (s) or cancel (c)")
        
        cv2.imshow(self.winname, self.canvas)
        
    def addLabel(self, x, y):
        '''
            添加标签
        '''
        if self.mp == MP_UNMARK:
            # 当前标注的是棋子脚底
            self.fchess = (x, y)
            # 更新状态码
            self.mp = MP_MARKED_FCHESS
        
        elif self.mp == MP_MARKED_FCHESS:
            # 当前标注的是盒子的中心
            self.cbox = (x, y)
            # 更新状态码
            self.mp = MP_MARKED_CBOX
        else:
            print("标注已完成")

        '''
        # 打印标注信息
        print("fchess")
        print(self.fchess)
        print("cbox")
        print(self.cbox)
        print("mp")
        print(self.mp)
        '''
        self.updateCanvas()
        
    def isMarkDone(self):
        '''
            返回是否标注完成
        '''
        return self.mp == MP_MARKED_CBOX

    def saveImg(self):
        '''
            保存图片
        '''
        # 保存样本素材
        cv2.imwrite(self.save_path + self.img_name, self.img)
        # 保存标注后的图片
        cv2.imwrite(self.save_path + 'log/' + self.img_name, self.canvas)

    def label2string(self):
        '''
            将标签转换为字符串, 用于保存在label.txt中
        '''
        (x1, y1) = self.fchess
        (x2, y2) = self.cbox
        return ",".join([self.img_name, str(x1), str(y1), str(x2), str(y2)]) + '\n'
    
    def saveLabelInfo(self):
        '''
            添加标注信息 追加模式
        '''
        with open(self.label_filename, 'a+') as f:
            f.write(self.label2string())
        
    def onDestroy(self):
        # 关闭窗口
        cv2.destroyWindow(self.winname)
import cv2 as cv 
import numpy as np

# HSV 颜色空间下棋子轮廓阈值 
lower = np.array([105,25,45])  
upper = np.array([135,125,130])
# HSV 颜色空间下棋子轮廓阈值 

kernel = np.ones((5,5),np.uint8) # 膨胀 腐蚀 操作的卷积核


class jumpmaster:

    def __init__(self):   # 设置全局变量
        self.roi = None   # 保存ROI图像变量
        self.chess_pos = None  # 保存棋子位置变量
        self.box_pos = None   # 保存盒子位置变量
        self.che_wh = None 
        self.box1_pos = None
        self.box2_pos = None
        self.box3_pos = None
        self.canvas = None  # 画布
        
    def findChess(self,img): # 注释规范 ：  操作名称  +  操作作用
        self.canvas = img  # 复制图像到画布 因为添加
        roi = img[300:600,:] # 截取ROI图像 作为主要分析对象
        self.roi = roi  # 将ROI图像作为全局变量 方便其他函数的使用
        hsv = cv.cvtColor(roi,cv.COLOR_BGR2HSV) # 转换颜色空间 BGR TO HSV
        bin_img = cv.inRange(hsv,lower,upper) # 阈值分割 因棋子颜色在游戏运行中稳定 采用阈值分割 跟踪棋子
        dliate = cv.dilate(bin_img,kernel,iterations = 2) # 膨胀 将图像膨胀 使得棋子头部和下体连在一起 后面的FindContours函数要用
        erode = cv.erode(dliate,kernel,iterations = 1) # 腐蚀 能够消除二值分割时的图像噪点 得到干净的轮廓图像 使用技巧吧这是
        bin_im,contours,hierarchy = cv.findContours(erode,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE) # 寻找轮廓 如果前面得到干净的二值轮廓 那现在轮廓就只有棋子了
        for cnt in contours:
            x,y,w,h = cv.boundingRect(cnt) # 对轮廓分析 得到最大包围矩形信息 长 宽 高等坐标
            area = w*h
            if area>4000 and area < 5700: # 软件面积滤波 过滤调一些小的不是棋子的色块
                self.chess_pos = (x,y)  # 棋子的坐标位置  注意这里的位置的是从看的角度出发的 不是从数组的角度出发的 但是可视化时要转化成从数组的角度的
                self.che_wh = (w,h)  # 棋子的高和宽
                #print("chess position is : x:{},y:{}".format(x+w/2,y+h))  # 调试信息语句
                return x+w/2,y+h  # 返回棋子底部中心坐标

    def findBox(self):  # 找到盒子的位置 自己发挥的 算法不好 有时候识别不到盒子
        stop = 0  # 标志变量
        edges = cv.Canny(self.roi,100,200)  # Canny 算子提取边缘
        che_x,che_y = self.chess_pos  # 根据棋子的位置将它周围的像素点设为0 因为通过观察有时候棋子的位置会超过盒子 造成识别错误
        for s in range(che_y,che_y + 100):
            # find box pointe1 y1
            for d in range(che_x-20,che_x + 90):
                edges[s][d] = 0 # 将棋子周围像素点设为0 避免下一步的识别盒子
        cv.imshow("edgess",edges) # 调试图片

        for r,i in enumerate(edges):  # 遍历盒子二值轮廓图像 找到盒子最顶点
            for c,j in enumerate(i):  
                if j == 255:
                    stop = 1
                    self.box_pos = (r,c)
                    break
            if stop == 1: 
                break
        cv.circle(self.roi,(c,r),6,(0,0,255),-1)

        # o is the array data    k is the number
        for k,o in enumerate(edges[r+20]):
            if o == 255:
                #print("x2:",k,"y2:",r+10)
                cv.circle(self.roi,(k,r+20),6,(0,0,255),-1)
                break
        # box pointe two
        
        for q,o in enumerate(edges[r+20][::-1]):
            if o == 255:
                
                cv.circle(self.roi,(700-q,r+20),6,(0,0,255),-1)
                break


        x1 = k 
        x2 = 700-q
        x3 = int((x2 - x1)/2)+k
        y3 = r+45
        x1 = k
        y1 = r+20
        x2 = 700-q
        y2 = r+20
        cv.line(self.roi,(c,r),(x1,y1),(0,0,255),4)
        cv.line(self.roi,(c,r),(x2,y2),(0,0,255),4)
        cv.line(self.roi,(x1,y1),(x2,y2),(0,0,255),4)
        cv.circle(self.roi,(x3,y3),6,(0,0,255),-1)
        cv.line(self.roi,(c,r),(x3,y3),(0,0,255),4)
        self.box3_pos = x3,y3
        self.box1_pos = k,y1
        self.box2_pos = x2,y2
        
        #print("x1:",x1,"x2 :",x2,"mid: ",int((x2-x1)/2)+x1)
        '''
        for q,o in enumerate(edges[r+20,k+10:]):
            this_data = o
            next_data = edges[r+10][q+1]
            if (this_data == 255) and (next_data == 0):
                cv.circle(self.roi,(k+q+10,r+10),6,(0,0,255),-1)
                break
        '''
        cv.imshow('canvas2',self.roi)
        return r,c

    def visual(self):     # 专门用来可视化操作的成员函数
        canvas = self.roi 
        che_x,che_y = self.chess_pos
        che_w,che_h = self.che_wh
        box_y,box_x = self.box_pos
        x3,y3 = self.box3_pos
        #cv.line(canvas,(che_x+int(che_w/2),che_y+che_h),(box_x,box_y+50),(0,0,255),5)
        #consider why change self.roi and the canvas same
        cv.line(canvas,(che_x+int(che_w/2),che_y+che_h),(x3,y3),(0,0,255),4)
        cv.imshow("visual",canvas)
        cv.imshow("222",self.canvas)

if __name__ == "__main__":
    # follow code use to test api
    img_indx = 0
    jum = jumpmaster()
    while True:
        stop = 0
        img = cv.imread("../test_data/"+str(img_indx)+".png",-1)
        canvas = np.copy(img)
        jum.findChess(img)
        r,c = jum.findBox()
        cv.circle(canvas,(c,r+300),6,(255,0,0),-1)
        cv.imshow("canvas",canvas)
        
        '''
        edges = cv.Canny(roi,100,200)
        cv.circle(roi,(c,r),6,(0,0,255),-1)  # why?
        cv.circle(roi,(c,r+50),6,(0,0,255),-1)
        cv.imshow("roi",roi)
        cv.imshow("edge",edges)  
        '''
        img_indx +=1         
        key_num = cv.waitKey(0)
        if key_num == ord("n"):
            continue
        if key_num == ord("s"):
            break
    cv.destroyAllWindows()
    
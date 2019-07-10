import cv2 as cv 
import numpy as np
import math
# HSV 颜色空间下棋子轮廓阈值 
lower = np.array([105,25,45])  
upper = np.array([135,125,130])
# HSV 颜色空间下棋子轮廓阈值 
kernel = np.ones((5,5),np.uint8) # 膨胀 腐蚀 操作的卷积核

class jumpmaster:
    
    def __init__(self):   # 设置全局变量
        self.roi = None   # 保存ROI图像变量
        self.chess_pos = None  # 保存棋子位置变量 棋子boudingRect的坐标
        self.chess_pos1 = None # 棋子底部中心点坐标
        self.box_pos = None   # 保存盒子位置变量
        self.che_wh = None 
        self.box_mask = None
        self.top_point = None
        self.rightest_point = None
        self.leftest_point = None
        self.bottom_point = None
        self.mid_point = None 
        self.canvas = None  # 画布

    def cal_singlechannel_mask(self,img,channel): # 计算单一通道颜色阈值
        hist_img = cv.calcHist([img],[channel],None,[256],[0,255])
        hist_img = np.array(hist_img)
        shang_data = 0
        right_data = 0
        for index,value in enumerate(hist_img):
            right_data = value
            if(shang_data == 0 and  right_data != 0):
                down = index
            if(right_data == 0 and shang_data != 0):
                up = index
            shang_data = right_data
        return down,up
    
    def cal_mask(self,img,channel): #计算游戏背景蒙版
        hist_img = cv.calcHist([img],[channel],None,[256],[0,255])
        hist_img = np.array(hist_img)
        shang_data = 0
        right_data = 0
        for index,value in enumerate(hist_img):
            right_data = value
            if(shang_data == 0 and  right_data != 0):
                down = index
            if(right_data == 0 and shang_data != 0):
                up = index
            shang_data = right_data
        return down,up

    def preprocess(self,img): # 预先处理分析游戏背景阈值 
        img_roi = img[200:500,695:700]  # 截取的roi 用作分析直方图
        #cv.imshow("img_ro2",img_ro2)
        (b_down,b_up) = self.cal_mask(img_roi,0)
        (g_down,g_up) = self.cal_mask(img_roi,1)
        (r_down,r_up) = self.cal_mask(img_roi,2)
        upper = np.array([b_up,g_up,r_up]) 
        downer = np.array([b_down-5,g_down-5,r_down-5]) 
        img_bin = cv.inRange(img,downer,upper)
        img_bin = cv.bitwise_not(img_bin)
        img_bin = cv.cvtColor(img_bin,cv.COLOR_GRAY2BGR)
        img = cv.bitwise_and(img,img_bin)
        return img

    def findChess(self,img): # 注释规范 ：  操作名称  +  操作作用
        self.canvas = img  # 复制图像到画布 直接对Img作图会改变数据
        img = self.preprocess(img) # 经过预处理 在盒子位置分离了游戏背景
        roi = img[300:600,:] # 截取ROI图像 作为主要分析对象
        self.roi = roi  # 将ROI图像作为全局变量 方便其他函数的使用
        #self.roi2 = img[300:500,:]
        hsv = cv.cvtColor(roi,cv.COLOR_BGR2HSV) # 转换颜色空间 BGR TO HSV
        bin_img = cv.inRange(hsv,lower,upper) # 阈值分割 因棋子颜色在游戏运行中稳定 采用阈值分割 跟踪棋子
        dliate = cv.dilate(bin_img,kernel,iterations = 2) # 膨胀 将图像膨胀 使得棋子头部和下体连在一起 后面的FindContours函数要用
        erode = cv.erode(dliate,kernel,iterations = 1) # 腐蚀 能够消除二值分割时的图像噪点 得到干净的轮廓图像 使用技巧吧这是
        contours,hierarchy = cv.findContours(erode,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE) # 寻找轮廓 如果前面得到干净的二值轮廓 那现在轮廓就只有棋子了
        for cnt in contours:
            x,y,w,h = cv.boundingRect(cnt) # 对轮廓分析 得到最大包围矩形信息 长 宽 高等坐标
            area = w*h
            if area>4000 and area < 5700: # 软件面积滤波 过滤调一些小的不是棋子的色块
                self.chess_pos = (x,y)  # 棋子的坐标位置  注意这里的位置的是从看的角度出发的 不是从数组的角度出发的 但是可视化时要转化成从数组的角度的
                self.che_wh = (w,h)  # 棋子的高和宽
                #print("chess position is : x:{},y:{}".format(x+w/2,y+h))  # 调试信息语句
                #self.chess_pos1 = (int(x+w/2),int(y+h)) # 记录棋子底部中心坐标，方便测试
                return x+w/2,y+h  # 返回棋子底部中心坐标

    def findBox(self):  # 找到盒子的位置 自己发挥的 算法不好 有时候识别不到盒子
        stop = 0  # 标志变量
        last = 0
        #cv.imshow("self.roi",self.roi)
        edges = cv.Canny(self.roi,100,200)  # Canny 算子提取边缘
        canvas = self.roi
        che_x,che_y = self.chess_pos  # 根据棋子的boundingRect将它周围的像素点设为0 因为通过观察有时候棋子的位置会超过盒子 造成识别错误
        for s in range(che_y,che_y + 100):
            # find box pointe1 y1
            for d in range(che_x-2,che_x + 50):
                edges[s][d] = 0 # 将棋子周围像素点设为0 避免下一步的识别盒子
        #cv.imshow("edgess",edges) # 调试图片
        cv.imshow("edges",edges)
        for r,i in enumerate(edges):  # 遍历盒子二值轮廓图像 找到盒子最顶点
            for c,j in enumerate(i):  
                if j == 255:
                    stop = 1
                    self.box_pos = (r,c)
                    break
            if stop == 1: 
                break
        topx = c
        topy = r
        #cv.circle(canvas,(c,r),6,(0,0,255),-1) #测试时用

        # o 是数组数据 K是行标
        now = 599
        last = 600  # 两个标志变量 刚开始随便赋值 这两个用来比较上一行和这一行的白点的行标 
        for leftest_point in range(300-r):          #得到在顶点往下还有多少行
            for k,o in enumerate(edges[r+leftest_point]): #遍历整个图像 寻找最左点 据观察 盒子的像素点都是一点一点的
                if o == 255:
                    #edges[r+leftest_point+1,k-1] = 255
                    now = k
                    break  
            if now >= last: 
                #cv.circle(canvas,(k,r+leftest_point),6,(0,0,255),-1) # 测试时用
                leftx = k 
                lefty = r+leftest_point
                break
            last = now        
    
        # the rightest point of box
        now = 599
        last = 600
        for rightest_point in range(300-r):
            for q,o in enumerate(edges[r+rightest_point][::-1]):
                if o == 255:
                    now = q
                    break 
            if now >= last:
                #cv.circle(canvas,(700-q,r+rightest_point),6,(0,0,255),-1) # 测试时用
                rightx = 700-q
                righty = r+rightest_point
                break
            last = now  
       

        if (leftx > topx) and (rightx >topx) :     # 都在右边
            midx = topx 
            midy = righty

        if (leftx < topx) and (rightx > topx) :
            midx = int((rightx - leftx)/2)+leftx
            midy = int((righty - lefty)/2)+lefty
        
        if( leftx < topx) and (rightx < topx) :
            midx = topx 
            midy = lefty

        
        
        # yyyy= math.sqrt((midx-topx)**2+(midy-topy)**2) # 不做过多运算 算了

        bottomx =   (midx-topx)+midx
        bottomy =   (midy-topy)+midy

        self.mid_point = (midx,midy)
        self.bottom_point = (bottomx,bottomy)
        self.top_point = (topx,topy)
        self.leftest_point = (leftx,lefty)
        self.rightest_point = (rightx,righty)

        return midx,midy

    def visual(self):     # 专门用来可视化操作的成员函数
        canvas = self.roi 

        topx,topy = self.top_point
        rightx,righty = self.rightest_point
        leftx,lefty = self.leftest_point
        bottomx,bottomy = self.bottom_point
        midx,midy = self.mid_point

        cv.line(canvas,(topx,topy),(leftx,lefty),(0,0,255),4)
        cv.line(canvas,(topx,topy),(rightx,righty),(0,0,255),4)
        cv.line(canvas,(topx,topy),(midx,midy),(0,0,255),4)
        cv.line(canvas,(leftx,lefty),(rightx,righty),(0,0,255),4)
        cv.line(canvas,(midx,midy),(bottomx,bottomy),(0,0,255),4)
        cv.line(canvas,(leftx,lefty),(bottomx,bottomy),(0,0,255),4)
        cv.line(canvas,(rightx,righty),(bottomx,bottomy),(0,0,255),4)
        cv.imshow("visual",canvas)
        

if __name__ == "__main__":
    # follow code use to test api
    img_indx = 0
    jum = jumpmaster()
    while True:
        stop = 0
        img = cv.imread("../DataSet/"+str(img_indx)+".png",1)
        canvas = np.copy(img)
        jum.findChess(img)
        r,c = jum.findBox()
        cv.circle(canvas,(c,r+300),6,(255,0,0),-1)
        cv.imshow("canvas",canvas)
        
        img_indx +=1         
        key_num = cv.waitKey(0)
        if key_num == ord("n"):
            continue
        if key_num == ord("s"):
            break
    cv.destroyAllWindows()
    
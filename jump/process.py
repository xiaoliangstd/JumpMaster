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
        self.mask_val = None # 直方图标志变量， 初始先选定左边作为检测 如果上一次盒子顶点在左 则右 类推 1 左 2 右
        self.index = 0

        self.final = None

        self.visual_chess = None

    '''
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
    '''
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
        self.final = np.copy(img)
        if self.mask_val == 2:
            img_roi = img[200:500,695:700]  # 截取的roi 用作分析直方图
            print(2)
        else :
            img_roi = img[200:500,0:5]
            print(1)
        (b_down,b_up) = self.cal_mask(img_roi,0)
        (g_down,g_up) = self.cal_mask(img_roi,1)
        (r_down,r_up) = self.cal_mask(img_roi,2)
        upper = np.array([b_up,g_up,r_up]) 
        downer = np.array([b_down-5,g_down-5,r_down-5]) 
        #print(downer,upper)
        img_bin = cv.inRange(img,downer,upper)
        img_bin = cv.bitwise_not(img_bin)
        img_bin = cv.cvtColor(img_bin,cv.COLOR_GRAY2BGR)
        img = cv.bitwise_and(img,img_bin)
        self.mask = cv.bitwise_and(img,img_bin)
        cv.imshow("mask",img)
        cv.imwrite("/home/liang/jumpmaster/picture/mask/"+"mask"+str(self.index)+".png",self.mask)
        return img

    def findChess(self,img): # 注释规范 ：  操作名称  +  操作作用
        #self.final = np.copy(img ) # 复制图像到画布 直接对Img作图会改变数据
        self.canvas = np.copy(img )
        #cv.imshow("liang",self.np.copy(img ))
        # 
        
        
        img = self.preprocess(img) # 经过预处理 在盒子位置分离了游戏背景
        roi = img[200:600,:] # 截取ROI图像 作为主要分析对象
        #roi = img # 截取ROI图像 作为主要分析对象
        self.roi = roi  # 将ROI图像作为全局变量 方便其他函数的使用


        hsv = cv.cvtColor(self.roi,cv.COLOR_BGR2HSV) # 转换颜色空间 BGR TO HSV
        bin_img = cv.inRange(hsv,lower,upper) # 阈值分割 因棋子颜色在游戏运行中稳定 采用阈值分割 跟踪棋子
        dliate = cv.dilate(bin_img,kernel,iterations = 2) # 膨胀 将图像膨胀 使得棋子头部和下体连在一起 后面的FindContours函数要用
        erode = cv.erode(dliate,kernel,iterations = 2) # 腐蚀 能够消除二值分割时的图像噪点 得到干净的轮廓图像 使用技巧吧这是
        # 素材用
        hsv1 = cv.cvtColor(self.canvas,cv.COLOR_BGR2HSV) # 转换颜色空间 BGR TO HSV
        bin_img1 = cv.inRange(hsv1,lower,upper) # 阈值分割 因棋子颜色在游戏运行中稳定 采用阈值分割 跟踪棋子
        dliate1 = cv.dilate(bin_img1,kernel,iterations = 2) # 膨胀 将图像膨胀 使得棋子头部和下体连在一起 后面的FindContours函数要用
        self.visual_chess = cv.erode(dliate1,kernel,iterations = 2) # 腐蚀 能够消除二值分割时的图像噪点 得到干净的轮廓图像 使用技巧吧这是
        # 素材用
        #cv.imshow("chess",erode1)
        
        contours,hierarchy = cv.findContours(erode,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE) # 寻找轮廓 如果前面得到干净的二值轮廓 那现在轮廓就只有棋子了
        for cnt in contours:
            x,y,w,h = cv.boundingRect(cnt) # 对轮廓分析 得到最大包围矩形信息 长 宽 高等坐标
            area = w*h
            if area>4000 and area < 6500: # 软件面积滤波 过滤调一些小的不是棋子的色块
                self.chess_pos = (x,y)  # 棋子的坐标位置  注意这里的位置的是从看的角度出发的 不是从数组的角度出发的 但是可视化时要转化成从数组的角度的
                self.che_wh = (w,h)  # 棋子的高和宽
                #print("chess position is : x:{},y:{}".format(x+w/2,y+h))  # 调试信息语句
                self.chess_pos1 = (int(x+w/2),int(y+h)) # 记录棋子底部中心坐标，方便测试
                cv.circle(self.final,(int(x+w/2),int(y+200+h)),10,(0,0,255),-1)
                cv.rectangle(self.final,(x,y+200),(x+w,y+200+h),(0,0,255),3)
                
                return x+w/2,y+h  # 返回棋子底部中心坐标

    def findBox(self):  
        stop = 0  # 标志变量
        last = 0
        #cv.imshow("self.roi",self.roi)
        edges = cv.Canny(self.roi,100,200)  # Canny 算子提取边缘
       
        canvas = self.roi
        che_x,che_y = self.chess_pos  # 根据棋子的boundingRect将它周围的像素点设为0 因为通过观察有时候棋子的位置会超过盒子 造成识别错误
        for s in range(che_y-10,che_y + 100):
            # find box pointe1 y1
            for d in range(che_x-2,che_x + 60):
                edges[s][d] = 0 # 将棋子周围像素点设为0 避免下一步的识别盒子

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
        if(topx >= 350):
            self.mask_val = 1
        else:
            self.mask_val = 2
        cv.circle(canvas,(c,r),6,(0,0,255),-1) #测试时用

        # o 是数组数据 K是行标
        now = 599
        last = 600  # 两个标志变量 刚开始随便赋值 这两个用来比较上一行和这一行的白点的行标 
        for leftest_point in range(400-r):          #得到在顶点往下还有多少行
            for k,o in enumerate(edges[r+leftest_point]): #遍历整个图像 寻找最左点 据观察 盒子的像素点都是一点一点的
                if o == 255:
                    #edges[r+leftest_point+1,k-1] = 255
                    now = k
                    break  
            if now >= last: 
                cv.circle(canvas,(k,r+leftest_point),6,(0,0,255),-1) # 测试时用
                leftx = k 
                lefty = r+leftest_point
                break
            last = now        

        # the rightest point of box
        now = 599
        last = 600
        for rightest_point in range(400-r):
            for q,o in enumerate(edges[r+rightest_point][::-1]):
                if o == 255:
                    now = q
                    break 
            if now == 0:
                rightx = 700
                righty = r+rightest_point
                break
            if now >= last:
                rightx = 700-q
                righty = r+rightest_point
                break
            last = now  
        #cv.circle(canvas,(rightx,righty),6,(0,0,255),-1) #测试时用
        # 过滤 因为会存在 盒子左边点连一块的情况
        
        if (lefty - topy) - (righty - topy) > 40:
            leftx = topx - (rightx-topx)
            lefty = righty

        if (leftx > topx) and (rightx >topx) :     # 都在右边
            midx = topx 
            midy = righty

        if( leftx < topx) and (rightx < topx) :
            midx = topx 
            midy = lefty

        if( leftx < topx) and (rightx > topx) :
            midx = int((rightx - leftx)/2)+leftx
            midy = int((righty - lefty)/2)+lefty
        
        # yyyy= math.sqrt((midx-topx)**2+(midy-topy)**2) # 不做过多运算 算了

        bottomx =   (midx-topx)+midx
        bottomy =   (midy-topy)+midy

        # 下面的语句主要用作visual语句的可视化
        self.mid_point = (midx,midy)
        self.bottom_point = (bottomx,bottomy)
        self.top_point = (topx,topy)
        self.leftest_point = (leftx,lefty)
        self.rightest_point = (rightx,righty)
        cv.circle(self.mask,(midx,midy+200),10,(203,192,255 ),-1)
        cv.circle(self.mask,(bottomx,bottomy+200),10,(203,192,255 ),-1)
        cv.circle(self.mask,(topx,topy+200),10,(203,192,255 ),-1)
        cv.circle(self.mask,(leftx,lefty+200),10,(203,192,255 ),-1)
        cv.circle(self.mask,(rightx,righty+200),10,(203,192,255 ),-1)

        cv.circle(self.final,(midx,midy+200),10,(203,192,255 ),-1)
        cv.circle(self.final,(bottomx,bottomy+200),10,(203,192,255 ),-1)
        cv.circle(self.final,(topx,topy+200),10,(203,192,255 ),-1)
        cv.circle(self.final,(leftx,lefty+200),10,(203,192,255 ),-1)
        cv.circle(self.final,(rightx,righty+200),10,(203,192,255 ),-1)

        cv.imshow("box_point",self.mask)
        cv.imwrite("/home/liang/jumpmaster/picture/box_point/"+"box_point"+str(self.index)+".png",self.mask)
        cv.line(self.mask,(topx,topy+200),(leftx,lefty+200),(203,192,255 ),4)
        cv.line(self.mask,(topx,topy+200),(rightx,righty+200),(203,192,255 ),4)
        cv.line(self.mask,(topx,topy+200),(midx,midy+200),(203,192,255 ),4)
        cv.line(self.mask,(leftx,lefty+200),(rightx,righty+200),(203,192,255 ),4)
        cv.line(self.mask,(midx,midy+200),(bottomx,bottomy+200),(203,192,255 ),4)
        cv.line(self.mask,(leftx,lefty+200),(bottomx,bottomy+200),(203,192,255 ),4)
        cv.line(self.mask,(rightx,righty+200),(bottomx,bottomy+200),(203,192,255 ),4)


        cv.line(self.final,(topx,topy+200),(leftx,lefty+200),(203,192,255 ),4)
        cv.line(self.final,(topx,topy+200),(rightx,righty+200),(203,192,255 ),4)
        cv.line(self.final,(topx,topy+200),(midx,midy+200),(203,192,255 ),4)
        cv.line(self.final,(leftx,lefty+200),(rightx,righty+200),(203,192,255 ),4)
        cv.line(self.final,(midx,midy+200),(bottomx,bottomy+200),(203,192,255 ),4)
        cv.line(self.final,(leftx,lefty+200),(bottomx,bottomy+200),(203,192,255 ),4)
        cv.line(self.final,(rightx,righty+200),(bottomx,bottomy+200),(203,192,255 ),4)
        chex,chey = self.chess_pos1
        cv.line(self.final,(midx,midy+200),(chex,chey+200),(255,0,0 ),4)
        cv.imwrite("/home/liang/jumpmaster/picture/final/"+"final"+str(self.index)+".png",self.final)
        cv.imshow("box_recon",self.mask)
        cv.imwrite("/home/liang/jumpmaster/picture/box_reco/"+"box_reco"+str(self.index)+".png",self.mask)
        #cv.circle(self.mask,)
        #cv.circle(self.mask,)
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

        x,y = self.chess_pos
        w,h = self.che_wh

        
        cv.imshow("final",self.final)

       
        cv.imshow("big_pic",self.canvas)
        cv.imshow("chess",self.visual_chess)
        cv.imwrite("/home/liang/jumpmaster/picture/big_pic/"+"big_pic"+str(self.index)+".png",self.canvas)
        chess_rcon = cv.rectangle(self.canvas,(x,y+200),(x+w,y+h+200),(0,0,255),6)
        cv.imshow("big_pic",self.canvas)
        cv.imshow("chess",self.visual_chess)
        cv.imwrite("/home/liang/jumpmaster/picture/chess_recon/"+"chess_recon"+str(self.index)+".png",chess_rcon)
        #self.index += 1
        cv.imwrite("/home/liang/jumpmaster/picture/chess/"+"chess"+str(self.index)+".png",self.visual_chess)

if __name__ == "__main__":
    # follow code use to test api
    img_indx = 0
    jum = jumpmaster()
    while True:
        stop = 0
        #img = cv.imread("../DataSet/"+str(img_indx)+".png",1)
        img = cv.imread("../DataSet/error11.png",1)
        cv.imshow("img",img)
        canvas = np.copy(img)
        jum.findChess(img)
        r,c = jum.findBox()
        cv.circle(canvas,(c,r+300),6,(255,0,0),-1)
        jum.visual()
        cv.imshow("canvas",canvas)
        
        img_indx +=1         
        key_num = cv.waitKey(0)
        if key_num == ord("n"):
            continue
        if key_num == ord("s"):
            break
    cv.destroyAllWindows()
    
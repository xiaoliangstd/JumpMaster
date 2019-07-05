import cv2 as cv 
import numpy as np 
import matplotlib.pyplot as plt


a = 0

def cal_mask(img,channel):

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
    

if __name__ == "__main__":

    while True:

        img = cv.imread("../test_data/"+str(a)+".png",1)
        #img_roi = img[200:540,695:700]  # 截取的roi 用作分析直方图
        #cv.imshow("img_ro2",img_ro2)
        (b_down,b_up) = cal_mask(img_roi,0)
        (g_down,g_up) = cal_mask(img_roi,1)
        (r_down,r_up) = cal_mask(img_roi,2)
        upper = np.array([b_up,g_up,r_up]) 
        downer = np.array([b_down-5,g_down-5,r_down-5]) 
        img_bin = cv.inRange(img,downer,upper)
        img_bin = cv.bitwise_not(img_bin)
        img_bin = cv.cvtColor(img_bin,cv.COLOR_GRAY2BGR)
        img = cv.bitwise_and(img,img_bin)
        cv.imshow("img",img)
        if cv.waitKey(0) == ord("n"):
            a += 1
            continue
        if cv.waitKey(0) == ord("m"):
            a -= 1
            continue
        if cv.waitKey(0) == ord("s"):
            break

    cv.waitKey(0)
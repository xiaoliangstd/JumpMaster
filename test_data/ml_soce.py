import cv2 as cv 
import numpy as np 
from sklearn import datasets
from sklearn.neighbors import KNeighborsClassifier

# mask  the key is use mask

lower = np.array([12,5,8])
upper = np.array([233,229,217])

digits = datasets.load_digits()


knnclf = KNeighborsClassifier(n_neighbors = 4)
knnclf.fit(digits.data,digits.target)
kernel = np.ones((3,3),np.uint8)

def ml_data(predice_img):
    predice_img = cv.dilate(predice_img,kernel,iterations = 1)
    
    predice_img = cv.erode(predice_img,kernel,iterations = 2)
    #cv.imshow("erode",predice_img)
    resize = cv.resize(predice_img,(8,8))
    #cv.imshow("num",resize)
    resize = resize/17
    return resize.reshape(64)


if __name__ == '__main__':

    for i in range(0,141):
        img = cv.imread(str(i)+".png",-1) 
        canvas = np.copy(img[50:200,0:300])
        img_hsv = cv.cvtColor(img[50:200,0:300],cv.COLOR_BGR2HSV) 
        img_bin = cv.inRange(img_hsv,lower,upper) 
        img_bin,contours,hier = cv.findContours(img_bin,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE) 
        pre_img = []
        ml_num = []
        for index,cnt in enumerate(contours):
            x,y,w,h = cv.boundingRect(cnt)
            cv.rectangle(canvas,(x,y),(x+w,y+h),(0,255,0),2)
            pre_img.append([img_bin[y-5:y+h+5,x-5:x+w+5],index])
            ml_num_predict = ml_data(img_bin[y-5:y+h+5,x-5:x+w+5])
            ml_num.append(ml_num_predict)
        
        predict = knnclf.predict(ml_num)
        print(predict)
        
        cv.imshow("canvas",canvas)
        cv.imshow("img",img_bin)
        key_num = cv.waitKey(0)
        if key_num == ord("n"):
            continue
        if key_num == ord("s"):
            break

    cv.destroyAllWindows()   


# -*- coding: utf-8 -*- 
'''
通过SelectROI 组件获取要识别的区域

因为没有必要处理所有的画面, 下一跳都在图像上方.


这里我们测的的ROI为
(166, 4, 325, 363)

从(166, 4)开始的, 宽度为325, 高度为363的矩形框.


接下来我们要批量处理其他的sample. 看roi是否满足.
'''


import cv2
import numpy as np

'''

选择一个矩形区域
如果要取消选中的话, 直接在旁边点击一下就好了

摁住 Space 选中 

也有文章说是Enter按键

'''


def select_game_roi(img_path):
 
    # Read image
    img = cv2.imread(img_path)
    
    cv2.imshow("image", img)
    # 是否显示网格 
    showCrosshair = True
    
    # 如果为Ture的话 , 则鼠标的其实位置就作为了roi的中心
    # False: 从左上角到右下角选中区域
    fromCenter = False
    # Select ROI
    r = cv2.selectROI("image", img, showCrosshair, fromCenter)

    print(r)
    # Crop image
    imCrop = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
 
    # Display cropped image
    cv2.imshow("image_roi", imCrop)
    cv2.imwrite("image_roi.png", imCrop)
    cv2.waitKey(0)


#测试, GUI的方式测量ROI
sample_01_path = "./samples/1.png"

select_game_roi(sample_01_path)



def select_all_sample_roi(sample_folder):

    from glob import glob

    r = (166, 4, 325, 363)

    sample_path_list = glob("%s/*.png"%(sample_folder))

    # 遍历所有的样本图片
    for sp in sample_path_list:
        img = cv2.imread(sp)

        imCrop = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

        cv2.imwrite('./samples_roi/%s'%(sp[len(sample_folder)+1:]), imCrop)

'''
将所有的测试样例, 按照roi截取
'''
'''
select_all_sample_roi("./samples")
'''
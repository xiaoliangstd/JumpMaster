'''
程序说明:
    从ADB中读取手机截图,并通过鼠标标注点, 保存标注文件
'''
import cv2
import numpy
import math
import os

# 样本标注
from SampleLabel import SampleLabel
# 凡哥写的ADBHelper类
from  ADBHelper import ADBHelper


# 图片保存路径 使用前先创建此文件夹/更新此参数
save_path = "./samples/label/"
# 样本标注信息文件名 使用前先创建此文件/更新此参数
label_filename = "./samples/label/labels.txt"


slabel = SampleLabel(save_path, label_filename)

# 初始化 ADBHelper, 填入手机屏幕宽度跟高度.
adb = ADBHelper(1080, 1920)


# 将距离转换成时间
def distance2time(distance):
    ratio = 1.53
    # 时间必须是整数类型
    return int(distance * ratio)

# 计算两点之间的距离
def cal_distance(pt1, pt2):
    '''
        获取棋子与下一跳盒子的距离
    '''
    (x1, y1) = pt1
    (x2, y2) = pt2
    return math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))

# 更新下一张图片 从ADB读入
def nextImg(slabel):
    '''
        使用迭代器， 遍历数组
    '''
    global adb
    try:
        # 从ADB读入图片
        img = adb.getScreenShotByADB()
        # 确认图片是否成功读入
        if img is None:
            return False
        else:
            slabel.updateImg(img, img_name=None)
            
            # 读入就将原来 unlabel的文件删除
        return True
    except StopIteration:
        print("遍历结束")
        return False

# 初始读入第一个
nextImg(slabel)
while True:
    keyValue = cv2.waitKey(0)
    # slabel.responseToKeyEvent(k, img=img)

    if keyValue == ord('e'):
        print('销毁窗口并保存')
        # 关闭窗口
        slabel.onDestroy()
        break

    elif keyValue == ord('n'):
        print("跳过，下一张图片")
        if not nextImg(slabel):
            # 如果获取失败， 退出
            break
    elif keyValue == ord('c'):
        print("取消标注")
        # update frame
        slabel.updateImg(slabel.img)

    elif keyValue == ord('s'):
        print("保存")
        if slabel.isMarkDone():
            # 保存样本
            slabel.saveImg()
            # 保存样本标注信息
            slabel.saveLabelInfo()
            # 显示提示信息 : 保存完成
            slabel.printProcessOnCanvas("Save Done")
            # 随机点击屏幕, 设置对应的延时时间.
            delay_time = distance2time(cal_distance(slabel.cbox, slabel.fchess))

            # 这里可以添加个延时
            # TODO

            adb.randPressOnScreen(delay_time)
            
            # 显示提示信息 : 自动载入下一张图片
            if not nextImg(slabel):
                # 如果获取失败， 退出
                break
        else:
            # 标注未完成， 无法保存
            slabel.printProcessOnCanvas("Error: mark undone, could not save")


    elif keyValue == ord('h'):

            print('''
            标注工具-帮助菜单
            ==================================
            键盘 n - next 下一张图片 需要手动更新!!!
            键盘 c - cancel 撤销标注
            键盘 s - save 保存样本标注与跳跃
            键盘 h - help 帮助菜单
            键盘 e - exit 保存标记并退出系统
            ''')
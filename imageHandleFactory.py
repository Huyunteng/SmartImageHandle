#!usr/bin/env python
# encoding:utf-8
'''
__Author__:沂水寒城
功能： Python opencv调用摄像头获取个人图片
使用方法：
    启动摄像头后需要借助键盘输入操作来完成图片的获取工作
    c(change): 生成存储目录
    p(photo): 执行截图
    q(quit): 退出拍摄
OpenCV简介
1、videoCapture()方法打开摄像
  摄像头变量 cv2.VideoCapture(n)  n为整数内置摄像头为0，若有其他摄像头则依次为1,2,3,...
  cap=cv2.VideoCapture(0) 打开内置摄像头
2、cap.isOpened()方法判断摄像头是否处于打开，返回结果为：True、False
3、ret,img=cap.read() 读取图像
  布尔变量,图像变量=cap.read()
4、cap.release() 释放摄像头
5、action=cv2.waitKey(n) 获取用户输入，同时可获取按键的ASCLL码值
'''
import datetime
import os
import re
import time
import aircv
import cv2
import numpy
from PIL import Image, ImageEnhance
from pytesseract import pytesseract
from BaseConfig import Config


def matchImg(imgsrc, imgobj, confidence=0.2) :
    """
    图片对比识别imgobj在imgsrc上的相对位置（批量识别统一图片中需要的部分）
    :param imgsrc: 原始图片路径(str)
    :param imgobj: 待查找图片路径（模板）(str)
    :param confidence: 识别度（0<confidence<1.0）
    :return: None or dict({'confidence': 相似度(float), 'rectangle': 原始图片上的矩形坐标(tuple), 'result': 中心坐标(tuple)})
    """
    match_result = aircv.find_template(imgsrc, imgobj, confidence)

    return match_result


def cutAndRecognizeImg(imgsrc, coordinate, enhance=2.5) :
    """
    根据坐标位置剪切图片
    :param imgsrc: 原始图片路径(str)
    :param out_img_name: 剪切输出图片路径(str)
    :param coordinate: 原始图片上的坐标(tuple) egg:(x, y, w, h) ---> x,y为矩形左上角坐标, w,h为右下角坐标
    :return:
    """
    image = Image.fromarray(cv2.cvtColor(
        imgsrc, cv2.COLOR_BGR2RGB))  # 将cv2的image转为PIL的image
    region = image.crop(coordinate)
    region = ImageEnhance.Contrast(region).enhance(enhance)
    # 识别
    code = pytesseract.image_to_string(region)
    # 专成cv2的Image
    region = cv2.cvtColor(numpy.asarray(region), cv2.COLOR_RGB2BGR)
    return region, code


def cameraAutoTakePictures(saveDir, _targetImagePaths, _resultimgpaths) :
    try :

        if not os.path.exists(saveDir) :
            os.makedirs(saveDir)
        config = Config("BaseConfig.ini")
        videoIndex = config.get_value("MachineInfo", "videoIndex")
        capture = cv2.VideoCapture(int(videoIndex))
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        capture.set(cv2.CAP_PROP_EXPOSURE, 0.7)
        capture.set(cv2.CAP_PROP_CONTRAST, 0.5)

        # while capture.isOpened():
        if capture.isOpened() :
            # time.sleep(2)
            ret, imgsrc = capture.read()

            if ret == True :
                dt = datetime.datetime.now()
                path = saveDir + dt.strftime("%Y%m%d%H%M%S") + '.jpg'
                cv2.imwrite(path, imgsrc)
                print("获取图像：" + path)
                dictRec = {}
                for _targetImagePath in _targetImagePaths :
                    filename = os.path.basename(_targetImagePath)
                    index = filename.rfind('.')
                    filename = filename[:index]

                    m1 = config.get_value(filename, "x1")
                    m2 = config.get_value(filename, "x2")
                    m3 = config.get_value(filename, "y1")
                    m4 = config.get_value(filename, "y2")
                    # print('%s,%s,%s,%s ' % (m1, m2, m3, m4))

                    imgobj = aircv.imread(_targetImagePath)  # 模板图片
                    rectangle = matchImg(imgsrc, imgobj, 0.2)['rectangle']  # 参数是匹配度
                    # print(rectangle)
                    w = rectangle[3][0] - rectangle[0][0]
                    h = rectangle[3][1] - rectangle[0][1]
                    x1 = rectangle[0][0] + int(m1)
                    x2 = rectangle[3][0] + int(m2)
                    y1 = rectangle[0][1] + int(m3)
                    y2 = rectangle[3][1] + int(m4)
                    # y1 = rectangle[0][1] + h / 3.5
                    # y2 = rectangle[3][1] - h / 5
                    # print(x1, y1, x2, y2, w, h)
                    region, code = cutAndRecognizeImg(imgsrc, (int(x1), int(y1), int(x2), int(y2)), 2.0)  # 参数是对比度
                    cv2.imwrite(_resultimgpaths[_targetImagePaths.index(_targetImagePath)] + dt.strftime(
                        "%Y%m%d%H%M%S") + '.jpg', region)
                    staticCode = re.findall(r"\d+\.?\d*", code)
                    staticCode = "".join(staticCode).strip()
                    if staticCode != '' :
                        dictRec[filename] = code
                    print(filename + " 处理前：" + code + " 处理后：" + staticCode)
                if (os.path.exists(path)) :
                    # os.remove(path)
                    print("删除图像：" + path)
                else :
                    print("删除图像失败：" + path)
                return dictRec
            else :
                raise Exception("Image Read Error!")
    except Exception as e :
        raise e
    finally :
        capture.release()  # 释放摄像头
        cv2.destroyAllWindows()  # 丢弃窗口

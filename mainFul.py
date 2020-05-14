# from CameraHandleFactory import *
# root_dir = os.path.dirname(os.path.abspath('.'))
import datetime
import sys
import traceback
from configparser import *
import os
import re
import time
import aircv
import cv2
import numpy
from PIL import Image, ImageEnhance
from pytesseract import pytesseract
from BaseConfig import Config
import requests
from suds.client import Client
import json


def WcfPost(Machinecode, MachineData):
    # wcf地址
    # http: // localhost: 62970 / HostServices.svc
    client = Client('http://192.168.1.93/HostServices.svc?wsdl')
    # print(client)
    # 查看可调用的wcf方法
    # print client  # 结果看图1
    # 调用wcf方法
    result = client.service.GetData()
    response = client.service.DasByImage(Machinecode, json.dumps(MachineData))
    return response


def matchImg(imgsrc, imgobj, confidence=0.2):
    """
    图片对比识别imgobj在imgsrc上的相对位置（批量识别统一图片中需要的部分）
    :param imgsrc: 原始图片路径(str)
    :param imgobj: 待查找图片路径（模板）(str)
    :param confidence: 识别度（0<confidence<1.0）
    :return: None or dict({'confidence': 相似度(float), 'rectangle': 原始图片上的矩形坐标(tuple), 'result': 中心坐标(tuple)})
    """
    match_result = aircv.find_template(imgsrc, imgobj, confidence)

    return match_result


def cutAndRecognizeImg(imgsrc, coordinate, enhance=2.5):
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


def cameraAutoTakePictures(saveDir, _targetImagePaths, _resultimgpaths):
    try:
        if not os.path.exists(saveDir):
            os.makedirs(saveDir)
        capture = cv2.VideoCapture(1)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        capture.set(cv2.CAP_PROP_EXPOSURE, 0.7)
        capture.set(cv2.CAP_PROP_CONTRAST, 0.5)

        # while capture.isOpened():
        if capture.isOpened():
            # time.sleep(2)
            ret, imgsrc = capture.read()

            if ret == True:
                dt = datetime.datetime.now()
                path = saveDir + dt.strftime("%Y%m%d%H%M%S") + '.jpg'
                cv2.imwrite(path, imgsrc)
                print(path)
                dictRec = {}
                for _targetImagePath in _targetImagePaths:
                    filename = os.path.basename(_targetImagePath)
                    index = filename.rfind('.')
                    filename = filename[:index]

                    m1 = Config.get_value(filename, "x1")
                    m2 = Config.get_value(filename, "x2")
                    m3 = Config.get_value(filename, "y1")
                    m4 = Config.get_value(filename, "y2")
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
                    dictRec[filename] = code
                    newcode = re.findall(r"\d+\.?\d*", code)
                    # print("".join(newcode).strip())
                    print(filename + " 处理前：" + code + " 处理后：" + "".join(newcode).strip())
                return dictRec
                # print(dictRec)
                # WcfPost()
                # os.remove(path)

            else:
                print("Image Read Error!")

            time.sleep(10)

        # capture.release()  # 释放摄像头
        # cv2.destroyAllWindows()  # 丢弃窗口

    except Exception:
        raise Exception
    finally:
        capture.release()  # 释放摄像头
        cv2.destroyAllWindows()  # 丢弃窗口


def fileHandle(MachineType):
    try:
        root_dir = os.path.dirname(os.path.abspath('..\\Host'))
        # _iniPath = root_dir + "\\BaseConfig.ini"
        # cf = configparser.ConfigParser()
        # cf.read(_iniPath)
        # machineType = cf.get("MachineInfo", "type")
        # 机床匹配目标文件夹
        _targetImagePath = root_dir + "\\MachineImages\\targetImage\\" + MachineType + "\\"

        if not os.path.exists(_targetImagePath):
            os.makedirs(_targetImagePath)
        # 机床结果文件夹
        _resultImagePath = root_dir + "\\MachineImages\\resultImage\\" + MachineType + "\\"

        if not os.path.exists(_resultImagePath):
            os.makedirs(_resultImagePath)
        # 机床照片
        _cameraImagePath = root_dir + "\\MachineImages\\cameraImage\\" + MachineType + "\\"

        if not os.path.exists(_cameraImagePath):
            os.makedirs(_cameraImagePath)
        # 查找所有的目标图片
        _targetImagePaths = get_all_files(_targetImagePath)
        # 根据目标图片创建result文件夹
        _resultimgpaths = []
        for file in _targetImagePaths:
            filename = os.path.basename(file)
            index = filename.rfind('.')
            filename = _resultImagePath + filename[:index] + "\\"
            _resultimgpaths.append(filename)
            if not os.path.exists(filename):
                os.makedirs(filename)
        return _cameraImagePath, _targetImagePaths, _resultimgpaths
    except Exception:
        raise Exception


def MesApiPost(MachineCode, MachineData):
    try:
        data = '{"ApiType": "EquipmentViewController","Parameters": [{"Value":"' + MachineCode + '"},{"Value":' + json.dumps(
            MachineData) + '}],"Method":"DasByImage","Context": {"InvOrgId": 321}}'
        jsondate = json.loads(data)
        response = requests.post(
            "http://localhost:8080/Server.svc/api/invoke", json=jsondate)
        print(response.text)
    except Exception as err:
        print(str(err))
    else:
        print('上传成功')


def get_all_files(dir):
    files_ = []
    list = os.listdir(dir)
    for i in range(0, len(list)):
        path = os.path.join(dir, list[i])
        if os.path.isdir(path):
            files_.extend(get_all_files(path))
        if os.path.isfile(path):
            files_.append(path)
    return files_


class Config():
    def __init__(self, ini_file_path):
        """
        :param ini_file_path: ini 文件的路径
        """
        self.config = ConfigParser()  # 实例化
        self.config.read(ini_file_path, encoding="utf-8")

    def get_section(self):
        """
        文件中 [baseconf] 这个就是节点，该方法是获取文件中所有节点，并生成列表
        :return: 返回内容-->> ['baseconf', 'concurrent']
        """
        sections = self.config.sections()
        return sections

    def get_option(self, section_name):
        """
        文件中 host,port... 这个就是选项，该方法是获取文件中某个节点中所有的选项，并生成列表
        :param section_name: 节点名称
        :return: section_name="baseconf" 返回内容-->> ['host', 'port', 'user', 'password', 'db_name']
        """
        option = self.config.options(section_name)
        return option

    def get_items(self, section_name):
        """
        该方法是获取文件中某个节点中的所有选项及对应的值
        :param section_name: 节点名称
        :return: section_name="baseconf" 返回内容-->> [('host', '127.0.0.1'), ('port', '11223')........]
        """
        option_items = self.config.items(section_name)
        return option_items

    def get_value(self, section_name, option_name):
        """
        该方法是获取文件中对应节点中对应选项的值
        :param section_name: 节点名称
        :param option_name: 选项名称
        :return: section_name="baseconf"，option_name='host' 返回内容-->> '127.0.0.1'
        """
        data_msg = self.config.get(section_name, option_name)
        return data_msg

    def set_value(self, section_name, option_name, value):
        """
        设置相关的值
        :param section_name: 节点名称
        :param option_name: 选项名称
        :param value: 选项对应的值
        :return:
        """
        self.config.set(section_name, option_name, value)
        # 举例： config.set("baseconf", 'host', 192.168.1.1)


Config = Config("BaseConfig.ini")
try:

    machineName = Config.get_value("MachineInfo", "name")
    machineType = Config.get_value("MachineInfo", "type")
    host = Config.get_value("MachineInfo", "host")
    _cameraImagePath, _targetImagePaths, _resultimgpaths = fileHandle(machineType)
    dictRec = cameraAutoTakePictures(_cameraImagePath, _targetImagePaths, _resultimgpaths)
    if not dictRec is None or dictRec.len > 0:
        response = WcfPost(machineName, dictRec)
        print(response)
except Exception as ex:
    ex_type, ex_val, ex_stack = sys.exc_info()
    print(ex_type)
    print(ex_val)
    for stack in traceback.extract_tb(ex_stack):
        print(stack)

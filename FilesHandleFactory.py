import os
import configparser

# 获取配置文件中的机床类型

# 文件夹处理
import sys

from FileHelper import *


def fileHandle(MachineType):
    try:
        # root_dir = os.path.dirname(os.path.abspath('../Host'))

        root_dir, filename = os.path.split(os.path.abspath(sys.argv[0]))
        realpath = os.path.realpath(sys.argv[0])
        _targetImagePath = root_dir + "/MachineImages/targetImage/" + MachineType + "/"

        if not os.path.exists(_targetImagePath):
            os.makedirs(_targetImagePath)
        # 机床结果文件夹
        _resultImagePath = root_dir + "/MachineImages/resultImage/" + MachineType + "/"

        if not os.path.exists(_resultImagePath):
            os.makedirs(_resultImagePath)
        # 机床照片
        _cameraImagePath = root_dir + "/MachineImages/cameraImage/" + MachineType + "/"

        if not os.path.exists(_cameraImagePath):
            os.makedirs(_cameraImagePath)
        # 查找所有的目标图片
        _targetImagePaths = get_all_files(_targetImagePath)
        # 根据目标图片创建result文件夹
        _resultimgpaths = []
        for file in _targetImagePaths:
            filename = os.path.basename(file)
            index = filename.rfind('.')
            filename = _resultImagePath + filename[:index] + "/"
            _resultimgpaths.append(filename)
            if not os.path.exists(filename):
                os.makedirs(filename)
        return _cameraImagePath, _targetImagePaths, _resultimgpaths
    except Exception:
        raise Exception

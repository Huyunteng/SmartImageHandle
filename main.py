# from CameraHandleFactory import *
# root_dir = os.path.dirname(os.path.abspath('.'))
import sys
import traceback
from threading import Timer
# from BaseConfig import Config
from imageHandleFactory import *
from FilesHandleFactory import *
# from wcfHostPost import *
from wcfHostPost import *
from BaseConfig import *

global imageProcessHandleTimer


class RepeatingTimer(Timer) :
    def run(self) :
        while not self.finished.is_set() :
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


def TakeImageHandler() :
    try :

        run = _myconfigger.get_value("MachineInfo", "run")
        # 0 开始;1 暂停;2 停止
        if run is None or run == '2' :
            print('程序退出')
            t.cancel()
            sys.exit(0)
        elif run == '1' :
            print('程序暂停')
        elif run == '0' :
            _machineName = _myconfigger.get_value("MachineInfo", "name")
            _machineType = _myconfigger.get_value("MachineInfo", "type")
            _host = _myconfigger.get_value("MachineInfo", "host")
            _cameraImagePath, _targetImagePaths, _resultimgpaths = fileHandle(_machineType)
            _imageRecognize = cameraAutoTakePictures(_cameraImagePath, _targetImagePaths, _resultimgpaths)
            if not _imageRecognize is None and len(_imageRecognize) > 0 :
                response = WcfPost(_machineName, _imageRecognize, _host)
                print(response)
            else :
                print('未能从图片中抓取到数据')
    except Exception as ex :
        # print(ex)
        ex_type, ex_val, ex_stack = sys.exc_info()
        # print(ex_type)
        print(ex_val)
        for stack in traceback.extract_tb(ex_stack) :
            print(stack)


_myconfigger = Config("BaseConfig.ini")
# interval = int(_myconfigger.get_value("MachineInfo", "interval"))
# t = RepeatingTimer(2.0, TakeImageHandler)
# t.start()
while 1 :
    try :
        run = _myconfigger.get_value("MachineInfo", "run")
        # 0 开始;1 暂停;2 停止
        if run is None or run == '2' :
            print('程序退出')
            # t.cancel()
            sys.exit(0)
        elif run == '1' :
            print('程序暂停')
        elif run == '0' :
            _machineName = _myconfigger.get_value("MachineInfo", "name")
            _machineType = _myconfigger.get_value("MachineInfo", "type")
            _host = _myconfigger.get_value("MachineInfo", "host")
            _cameraImagePath, _targetImagePaths, _resultimgpaths = fileHandle(_machineType)
            _imageRecognize = cameraAutoTakePictures(_cameraImagePath, _targetImagePaths, _resultimgpaths)
            if not _imageRecognize is None and len(_imageRecognize) > 0 :
                response = WcfPost(_machineName, _imageRecognize, _host)
                print(response)
            else :
                print('未能从图片中抓取到数据')
    except Exception as ex :
        # print(ex)
        ex_type, ex_val, ex_stack = sys.exc_info()
        # print(ex_type)
        print(ex_val)
        for stack in traceback.extract_tb(ex_stack) :
            print(stack)
    finally:
        time.sleep(10)

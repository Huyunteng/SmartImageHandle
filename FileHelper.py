import os


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
# def GetAllFiles():
#    #imageProcessHandleTimer.cancel()
#    _targetImagePaths = get_all_files(machineCapture)
#    for file in _targetImagePaths:
#            ImageProcessHandle(file)

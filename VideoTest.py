import sys
import traceback
import cv2
import numpy

try :
    index = 0
    cap = cv2.VideoCapture(index)  # 调整参数实现读取视频或调用摄像头
    print("Index:" + str(index))
    while 1 :
        print("readstart")
        ret, frame = cap.read()
        print("readend")
        cv2.imshow("cap", frame)
        if cv2.waitKey(100) & 0xff == ord('q') :
            break
    cap.release()
    cv2.destroyAllWindows()
except Exception as ex :
    ex_type, ex_val, ex_stack = sys.exc_info()
    print(ex_type)
    print(ex_val)
    for stack in traceback.extract_tb(ex_stack) :
        print(stack)

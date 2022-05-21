import numpy as np
import cv2 as cv
import os
import sys

if __name__ == "__main__":
    dayPath = sys.argv[1] if sys.argv[1][-1] == "/" else sys.argv[1] + "/"
    allPointPaths = []
    for d in os.listdir(dayPath):
        if "." not in d:
            allPointPaths.append(d)
    for p in allPointPaths:
        binaryPath = dayPath + p + "/binaryFITC/"
        try:
            os.mkdir(dayPath + p + "/cutBinary/")
            tgtPath = dayPath + p + "/cutBinary/"
        except Exception as e:
            print(e)
        for tifName in os.listdir(binaryPath):
            try:
                src = cv.imread(binaryPath + tifName)
                tgt = src[512:512+1024, 512:512+1024]
                cv.imwrite(tgtPath + tifName, tgt)
            except:
                print(e)
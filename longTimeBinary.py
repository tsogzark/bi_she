from pklAnalysis import longTimeBinary
import multiprocessing
import sys
import os
import cv2 as cv

def processPoint(path):
    print("processing " + path)
    fitcPath = path + "FITC/xyAdjust/recut/"
    # tritcPath = "./pointSets/12/TRITC/"
    fitcBinPath = path + "binaryFITC/"
    # tritcBinPath = "./pointSets/12/binaryTRITC/"
    try:
        os.mkdir(fitcBinPath)
    except Exception as e:
        print(e)

    # try:
    #     os.mkdir(tritcBinPath)
    # except Exception as e:
    #     print(e)

    fitcNames = os.listdir(fitcPath)
    # tritcNames = os.listdir(tritcPath)
    for name in fitcNames:
        if ".tif" in name:
            print(fitcPath + name)
            tmpImg = cv.imread(fitcPath + name, -1)
            tmpImg = longTimeBinary(tmpImg)
            cv.imwrite(fitcBinPath + list(name.split("-"))[0] + ".tif", tmpImg)

    # for name in [tritcNames[21], tritcNames[2]]:
    #     print(tritcPath + name)
    #     tmpImg = cv.imread(tritcPath + name, -1)
    #     tmpImg = longTimeBinary(tmpImg)
    #     cv.imwrite(tritcBinPath + list(name.split("-"))[0] + ".tif", tmpImg)

def processThreading(pathList):
    print("In longTimeBinary.py thread, Processing:")
    print("<_____---^_^---_____>")
    print(pathList)
    print("<_____---^_^---_____>")
    for path in pathList:
        processPoint(path)


if __name__ == "__main__":
    coreNum = int(sys.argv[2])
    pointSetsPath = "./pointSets/%s/" % sys.argv[1]
    allPathNames = os.listdir(pointSetsPath)
    pointPathNames = []
    for d in allPathNames:
        if "." not in d:
            pointPathNames.append(pointSetsPath + d + "/")
    step = int(len(pointPathNames)/coreNum) + 1
    pathsForth = []
    divNum = 0
    while divNum * step < len(pointPathNames):
        pathsForth.append(pointPathNames[divNum * step:min(len(pointPathNames), (divNum + 1) * step)])
        divNum += 1
    threads = []
    for paths in pathsForth:
        tmpTh = multiprocessing.Process(target=processThreading, args=(paths,))
        threads.append(tmpTh)
    for th in threads:
        th.start()

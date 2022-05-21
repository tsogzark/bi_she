import traceback
import csv
import os
import sys
from ctypes import util
from itertools import count
from platform import release
from re import template
from subprocess import TimeoutExpired
from unicodedata import category
from scipy import stats
import cv2
from delta import utilities as utils
import numpy as np
import pickle
import matplotlib.pyplot as plt
import multiprocessing

def getInternal(contours, cells, height, width):
    reDict = {}
    for i in range(len(cells)):
        tmpA = np.zeros((height, width), np.uint8)
        tmpA = cv2.drawContours(
            tmpA,
            contours,
            i,
            color=1,
            thickness=-1,
            offset=(0, 0)
        )
        reDict[cells[i]] = (np.array(np.where(tmpA == 1)).T)
    return reDict

def longTimeBinary(src):
    adth = np.zeros(src.shape, np.uint16)
    bian = 2**5
    for i in range(0, 2**10-bian):
        for j in range(0, 2**10-bian):
            tmpImg = src[i:i+bian, j:j+bian]
            ret, th = cv2.threshold(tmpImg, tmpImg.mean(), 2**16-1, cv2.THRESH_BINARY)
            th[np.where(th != 2**16-1)] = 0
            th[np.where(th == 2**16-1)] = 1
            adth[i:i+bian, j:j+bian] += th

    adth[np.where(adth > 512)] = 2**16-1  # 512=((2**5)^2)/2
    adth[np.where(adth <= 512)] = 0

    return adth


def getDivisionLengths(cellDict):
    divisionLengths = []
    for p in cellDict["0"]:
        lengths = p["length"]
        daughters = p["daughters"]
        for i in range(len(lengths)):
            if daughters[i] != None:
                divisionLengths.append(lengths[i-1])
    return divisionLengths


def getDivisionTimes(cellDict):
    divisionTimes = []
    for p in cellDict["0"]:
        daughters = p["daughters"]
        for i in range(len(daughters)):
            if daughters[i] != None:
                for j in range(i):
                    if daughters[i - j - 1] != None or j == i-1:
                        divisionTimes.append(j)
                        break
    return divisionTimes


def getCellDict(pklPath):
    with open(pklPath, "rb") as f:
        pkl = pickle.load(f)
    cellDict = {}
    n = 0
    for r, roi in enumerate(pkl.rois):
        cellDict[str(n)] = roi.lineage.cells
        n += 1
    return cellDict


def visualDivisionLength():
    pklPaths = [
        "./pointSets/20220323/15/delta_results/Position000000.pkl",
        "./pointSets/20220323/30/delta_results/Position000000.pkl"
    ]
    xTickNames = ["15", "30"]
    numOfPkl = len(pklPaths)
    cellDicts = []
    divisionLengths = []
    for i in range(numOfPkl):
        tmpCellDict = getCellDict(pklPaths[i])
        tmpDivisionLength = getDivisionLengths(tmpCellDict)
        cellDicts.append(tmpCellDict)
        divisionLengths.append(tmpDivisionLength)
    for i in range(numOfPkl):
        plt.scatter(np.random.normal(1+i, 0.01, size=len(divisionLengths[i])), divisionLengths[i])
    plt.boxplot(divisionLengths)
    plt.xticks([1, 2], xTickNames)
    plt.show()


def visualDivisionTime():
    pklPaths = [
        "./pointSets/20220323/15/delta_results/Position000000.pkl",
        "./pointSets/20220323/30/delta_results/Position000000.pkl"
    ]
    xTickNames = ["15", "30"]
    numOfPkl = len(pklPaths)
    cellDicts = []
    divisionTimes = []
    for i in range(numOfPkl):
        tmpCellDict = getCellDict(pklPaths[i])
        tmpDivisionTime = getDivisionTimes(tmpCellDict)
        cellDicts.append(tmpCellDict)
        divisionTimes.append(tmpDivisionTime)
    for i in range(numOfPkl):
        plt.scatter(np.random.normal(1+i, 0.01, size=len(divisionTimes[i])), divisionTimes[i])
    plt.boxplot(divisionTimes)
    plt.xticks([1, 2], xTickNames)
    plt.show()


def getIndexInFrame(cell, frameCells):
    matchList = []
    for i in range(len(cell["frame"])):
        for cell in frameCells[i]:
            if cell["new_pole"][i] in cell:
                matchList.append(i)
                break
    return matchList


def getIndexList(cells, frameCells):
    reList = []
    for cell in cells:
        reList.append(getIndexInFrame(cell, frameCells))
    return reList

def getFrameCells(path, pkl):
    DIR = path
    masks = pkl.rois[0].label_stack
    frameCells = []
    print(DIR)
    for i in range(len(masks)):
        print("processing " + str(i))
        cells, contours = utils.getcellsinframe(masks[i], return_contours=True)
        frameCells.append(getInternal(contours, cells, 1024, 1024))
    return frameCells


def checkPercent(img, points):
    maxGray = np.max(img)
    num = 0
    for p in points:
        if len(img.shape) != 2:
            if (img[p[0], p[1]] == [255,255,255]).all():
                num += 1
        else:
            if img[p[0], p[1]] == maxGray:
                num += 1

    return num/len(points)

def cellCon(img, cellContours):
    fitc = (img/np.max(img)*(2**8-1)).astype(np.uint8)
    fitcRGB = cv2.cvtColor(fitc, cv2.COLOR_GRAY2RGB)
    fitcRGB = cv2.drawContours(
        fitcRGB,
        cellContours,
        -1,
        color=(255, 255, 0),
        thickness=1,
        offset=(0, 0)
    )
    return fitcRGB

def identify(binaryPath, internalDicts):
    ifDicts = []
    for i in range(len(internalDicts)):
        greenOrRed = {"g":[], "r":[]}
        img = cv2.imread(binaryPath + str(i) + ".tif", -1)
        for key in internalDicts[i]:
            if checkPercent(img, internalDicts[i][key]) > 0.75:
                greenOrRed["g"].append(key)
            else:
                greenOrRed["r"].append(key)
        ifDicts.append(greenOrRed)
    return(ifDicts)

def writeColorCsv(path, colorList, cellNum, frameNum):
    DIR = path
    with open(DIR + "color.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["id"] + ["frame-"+str(x) for x in range(frameNum)])
        for i in range(cellNum):
            row = [i]
            for j in range(frameNum):
                if i in colorList[j]["g"]:
                    row.append(1)
                elif i in colorList[j]["r"]:
                    row.append(2)
                else:
                    row.append(0)
            writer.writerow(row)

def writeContactCsv(path, colorList, frameCells):
    DIR = path
    frames = len(frameCells)
    try:
        os.mkdir(DIR + "contact")
    except Exception as e:
        print(e)
    for i in range(frames):
        print("contact frame" + str(i))
        tmpG = {}
        tmpR = {}
        for g in colorList[i]["g"]:
            x = frameCells[i][g][:, 0].mean()
            y = frameCells[i][g][:, 1].mean()
            tmpG[g] = [x,y]
        for r in colorList[i]["r"]:
            x = frameCells[i][r][:, 0].mean()
            y = frameCells[i][r][:, 1].mean()
            tmpR[r] = [x,y]
        with open(DIR + "contact/frame" + str(i) + ".csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["id"])
            for keyG in tmpG:
                row = [keyG]
                for keyR in tmpR:
                    if getDistance(tmpG[keyG], tmpR[keyR]) < 100:
                        if getMinDistance(frameCells[i][keyG], frameCells[i][keyR]) < 10:
                            row.append(keyR)
                writer.writerow(row)

def getMinDistance(pointsA, pointsB):
    min = 4096
    for a in pointsA:
        for b in pointsB:
            if getDistance(a,b) < min:
                min = getDistance(a,b)
    return min

def getDistance(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.linalg.norm(v1 - v2)

def processPoint(path, pklPath, binaryFitcPath):
    with open(pklPath, "rb") as f:
        pkl = pickle.load(f)
    cells = pkl.rois[0].lineage.cells
    frameCells = getFrameCells(path, pkl)
    colorList = identify(binaryFitcPath, frameCells)
    writeColorCsv(path, colorList, len(cells), len(frameCells))
    writeContactCsv(path, colorList, frameCells)

def processThreading(pathList):
    print("In pklAnalysis.py thread, Processing:")
    print("<_____---^_^---_____>")
    print(pathList)
    print("<_____---^_^---_____>")
    for path in pathList:
        try:
            processPoint(
                    path,
                    path + "BF-1/xyAdjust/rename/delta_results/Position000000.pkl",
                    path + "binaryFITC/"
            )
        except Exception as e:
            traceback.print_exc()

# if __name__ == "__main__":
#     path = "./pointSets/20220331/"+ sys.argv[1] + "/"
#     processPoint(
#             path,
#             path + "BF-1/rename/delta_results/Position000000.pkl",
#             path + "binaryFITC/"
#     )

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
    # visualDivisionLength()
    # visualDivisionTime()

    # pklPath = "./pklFile/20220323.pkl"
    # with open(pklPath, "rb") as f:
    #     pkl = pickle.load(f)
    # cellDict = {}
    # n = 0
    # for r, roi in enumerate(pkl.rois):
    #     cellDict[str(n)] = roi.lineage.cells
    #     print(len(roi.label_stack))
    #     print(roi.label_stack[0])
    #     tmpA = np.array(roi.label_stack[0])
    #     # plt.imshow(tmpA, "gray")
    #     # plt.show()
    #     print(np.where(tmpA != 0))
    #     n += 1
    #
    # roi = pkl.rois[0]

    # if roi.box is None:
    #     xtl, ytl = (0, 0)
    # else:
    #     xtl, ytl = (roi.box["xtl"], roi.box["ytl"])
    # print(xtl, ytl)
    # masks = pkl.rois[0].label_stack
    # cells, contours = utils.getcellsinframe(masks[0], return_contours=True)
    # getInternal(contours, cells, 2048, 2048)
    # img = np.zeros((2048, 2048), dtype=np.uint8)
    # output = cv2.drawContours(
    #     img,
    #     contours,
    #     -1,
    #     color=255,
    #     thickness=-1,
    #     offset=(xtl, ytl)
    # )
    # plt.imshow(img)
    # plt.show()
    # print(contours)
    # print(cells)
    # print(len(pkl.rois))
    # print(cellDict["0"][2]["frames"])
    # print(cellDict["0"][2]["new_pole"])
    # print(cellDict["0"][2]["old_pole"])
    # print(cellDict["0"][2]["length"])
    # print(cellDict["0"][2]["daughters"])
    # listOfPoints = getInternal(contours, cells, 2048, 2048)

    # matchList = []
    # for p in cellDict["0"][2]["new_pole"][0]:
    #     for i in range(len(listOfPoints)):
    #         if p in listOfPoints[i]:
    #             matchList.append(i)
    #             listOfPoints.pop(i)
    #             break
    # print(matchList)

    # x = [1, 2, 3, 4, 5, 3, 3, 3]
    # plt.scatter([1 for i in range(8)], x)
    # plt.boxplot(x)
    # plt.show()

    # divisionLengths = []
    # for p in cellDict["0"]:
    #     lengths = p["length"]
    #     daughters = p["daughters"]
    #     for i in range(len(lengths)):
    #         if daughters[i] != None:
    #             divisionLengths.append(lengths[i-1])
    # plt.scatter(np.random.normal(1, 0.01, size=len(divisionLengths)), divisionLengths)
    # plt.boxplot(divisionLengths)
    # plt.show()

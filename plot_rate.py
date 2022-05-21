import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
import pickle
from delta import utilities as utils
import csv


def cellCon(img, cellContours, color, cellIndex):
    if len(img.shape) == 2:
        fitc = (img/np.max(img)*(2**8-1)).astype(np.uint8)
        fitcRGB = cv2.cvtColor(fitc, cv2.COLOR_GRAY2RGB)
    else:
        fitcRGB = img
    fitcRGB = cv2.drawContours(
        fitcRGB,
        cellContours,
        cellIndex,
        color=color,
        thickness=-1,
        offset=(0, 0)
    )
    return fitcRGB


if __name__ == "__main__":
    rate = []
    current_dir = os.path.dirname(__file__)
    path = "/pointSets/20220331/"
    for p in range(len(os.listdir(current_dir + path))):
        print(p)
        try:
            DIR = os.path.dirname(__file__) + path + str(p+1) + "/"
            colorCsvPath = DIR + "color.csv"
            pklPath = DIR + "BF-1/rename/delta_results/Position000000.pkl"
            try:
                os.mkdir(DIR + "composite")
            except Exception as e:
                print(e)
            binaryFitcPath = DIR + "binaryFITC/"
            contactPath = DIR + "contact/"

            data = pd.read_csv(colorCsvPath)
            dataList = np.array(data.values.tolist())
            turnList = []

            for i in range(len(dataList)):
                notFlag = 0
                existFlag = 0
                for j in range(1, len(dataList[i])):
                    if dataList[i][j] == 2 and dataList[i][j-1] == 1:
                        notFlag = 1
                    if dataList[i][j] == 1 and dataList[i][j-1] == 2 and j != 1:
                        existFlag = j
                try:
                    if not(dataList[i][existFlag-2]==2 
                          and dataList[i][existFlag-3]==2):
                        notFlag = 1
                except Exception as e:
                    print(e)
                    notFlag = 1
                if not notFlag:
                    if existFlag:
                        turnList.append(dataList[i])

            turnList = np.array(turnList)
            greenPos = np.where(turnList==1)[1]
            with open(pklPath, "rb") as f:
                pkl = pickle.load(f)

            masks = pkl.rois[0].label_stack
            lineageCells = pkl.rois[0].lineage.cells
            maxContactNum = 0
            for fi in range(25):
                print("process " + str(p) + ":" + str(fi))
                contactFramePath = DIR + "/contact/frame" + str(fi) + ".csv"
                currentContactNum = 0
                with open(contactFramePath, "r") as f:
                    lines = f.readlines()
                for line in lines:
                    currentContactNum += line.count(",")
                    if line.count(",") > maxContactNum:
                        maxContactNum = line.count(",")
                maxContactNum += currentContactNum

                cells, contours = utils.getcellsinframe(masks[fi], return_contours=True)
                target = dataList[:,fi+1]
                img = cv2.imread(binaryFitcPath + str(fi)+".tif", -1)
                font = cv2.FONT_HERSHEY_SIMPLEX
                for i in range(len(target)):
                    if target[i] == 1:
                        targetIndex = lineageCells[i]["frames"].index(fi)
                        poleY, poleX = lineageCells[i]["new_pole"][targetIndex]
                        img = cellCon(img, contours, (0, 200, 0), cells.index(i))
                        cv2.putText(
                          img,
                          text=str(i),
                          org=(poleX, poleY),
                          fontFace=font,
                          fontScale=0.2,
                          thickness=1,
                          lineType=cv2.LINE_AA,
                          color=(200,0,0)
                        )
                    if target[i] == 2:
                        targetIndex = lineageCells[i]["frames"].index(fi)
                        poleY, poleX = np.fix(0.5*(lineageCells[i]["new_pole"][targetIndex] + lineageCells[i]["old_pole"][targetIndex])).astype(np.uint)
                        img = cellCon(img, contours, (0, 0, 200), cells.index(i))
                        cv2.putText(
                          img,
                          text=str(i),
                          org=(poleX, poleY),
                          fontFace=font,
                          fontScale=0.2,
                          thickness=1,
                          lineType=cv2.LINE_AA,
                          color=(200,0,0)
                        )

                cv2.imwrite(DIR + "composite/" + str(fi) + "com.tif", img)
            rate.append(len(turnList)/25/maxContactNum)
        except Exception as e:
            print(e)
    with open(DIR + "rate.csv", "w") as f:
        writer = csv.writer(f)
        for r in rate:
            writer.writerow([str(r)])

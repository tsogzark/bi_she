import pandas as pd
import matplotlib as mpl
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


def process_day(point_path):
    rate = []
    for p in range(30):
        print(p)
        try:
            DIR = os.path.dirname(__file__) + point_path + str(p+1) + "/"
            colorCsvPath = DIR + "color.csv"
            # pklPath = DIR + "BF-1/rename/delta_results/Position000000.pkl"
            # try:
            #     os.mkdir(DIR + "composite")
            # except Exception as e:
            #     print(e)
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
                          and dataList[i][existFlag+1]==1
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
            # with open(pklPath, "rb") as f:
            #     pkl = pickle.load(f)

            # masks = pkl.rois[0].label_stack
            # lineageCells = pkl.rois[0].lineage.cells
            maxContactNum = 0
            count_frames = len(os.listdir(DIR + "contact"))
            for fi in range(count_frames):
                print("process " + str(p) + ":" + str(fi))
                contactFramePath = DIR + "contact/frame" + str(fi) + ".csv"
                currentContactNum = 0
                with open(contactFramePath, "r") as f:
                    lines = f.readlines()
                for line in lines:
                    # currentContactNum += line.count(",")
                    if line.count(",") > maxContactNum:
                        maxContactNum = line.count(",")
                # maxContactNum += currentContactNum

            #     cells, contours = utils.getcellsinframe(masks[fi], return_contours=True)
            #     target = dataList[:,fi+1]
            #     img = cv2.imread(binaryFitcPath + str(fi)+".tif", -1)
            #     font = cv2.FONT_HERSHEY_SIMPLEX
            #     for i in range(len(target)):
            #         if target[i] == 1:
            #             targetIndex = lineageCells[i]["frames"].index(fi)
            #             poleY, poleX = lineageCells[i]["new_pole"][targetIndex]
            #             img = cellCon(img, contours, (0, 200, 0), cells.index(i))
            #             cv2.putText(
            #               img,
            #               text=str(i),
            #               org=(poleX, poleY),
            #               fontFace=font,
            #               fontScale=0.2,
            #               thickness=1,
            #               lineType=cv2.LINE_AA,
            #               color=(200,0,0)
            #             )
            #         if target[i] == 2:
            #             targetIndex = lineageCells[i]["frames"].index(fi)
            #             poleY, poleX = np.fix(0.5*(lineageCells[i]["new_pole"][targetIndex] + lineageCells[i]["old_pole"][targetIndex])).astype(np.uint)
            #             img = cellCon(img, contours, (0, 0, 200), cells.index(i))
            #             cv2.putText(
            #               img,
            #               text=str(i),
            #               org=(poleX, poleY),
            #               fontFace=font,
            #               fontScale=0.2,
            #               thickness=1,
            #               lineType=cv2.LINE_AA,
            #               color=(200,0,0)
            #             )

            #     cv2.imwrite(DIR + "composite/" + str(fi) + "com.tif", img)
            rate.append(len(turnList)/25/maxContactNum)
        except Exception as e:
            print(e)
    with open(os.path.dirname(__file__) + point_path + "rate.csv", "w") as f:
        writer = csv.writer(f)
        for r in rate:
            writer.writerow([str(r)])
    return rate


def gen_box_data(data, xticks, max_tick):
    re = []
    xticks = [0] + xticks
    for i in range(len(xticks) - 1):
        for j in range(max(xticks[i + 1] - xticks[i] - 1, 0)):
            re.append([0])
        re.append(data[i])
    for i in range(max_tick - xticks[-1]):
        re.append([0])
    return re


if __name__ == "__main__":
    rateA = process_day("/pointSets/20220402/")
    rateB = process_day("/pointSets/20220412/")
    rateC = process_day("/20220414/")
    rateD = process_day("/pointSets/20220331/")
    src_data = [
        #rateA[0:int(len(rateA)/2)],
        #rateB[0:int(len(rateB)/2)],
        #rateC[0:int(len(rateC)/2)],
        rateD[0:int(len(rateD)/2)],
        rateB[int(len(rateB)/2):len(rateB)],
        rateA[int(len(rateA)/2):len(rateA)],
        rateC[int(len(rateC)/2):len(rateC)],
        #rateD[int(len(rateD)/2):len(rateD)]
    ]
    src_mean = [
        np.median(rateD[0:int(len(rateD)/2)]),
        np.median(rateB[int(len(rateB)/2):len(rateB)]),
        np.median(rateA[int(len(rateA)/2):len(rateA)]),
        np.median(rateC[int(len(rateC)/2):len(rateC)])
    ]
    data = gen_box_data(
            src_data,
            [0,12,25,36],
            50
            )
    calc_data = []
    with open("data.csv", "r") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            calc_data.append([float(x) for x in row])
    fig = plt.figure()
    ax = fig.gca()
    ax2 = ax.twinx()
    calc_show_data = 0.000075 * np.array(calc_data[0])
    lineA = ax2.plot([0.5*x+1 for x in range(101)], calc_show_data, "b", label="Simulated proteins")
    ax.boxplot(data)
    ax.violinplot(data)
    for i in range(len(data)):
        x = np.random.normal(i + 1, 0.05, size=len(data[i]))
        ax.plot(x, data[i], "r", alpha=0.2)
    lineB = ax.plot([0+1,12+1,25+1,36+1],src_mean, "gx", alpha=1, markersize=20, label="Rate Median")
    ax.tick_params(axis='y', labelsize=20)
    ax2.tick_params(axis='y', labelsize=20)
    ax.set_xticks([x for x in range(1, 51, 5)])
    ax.set_xticklabels([x for x in range(0, 50, 5)], fontsize=20)
    ax.set_xlabel("Kanamycin/(mg/L)", fontsize=20)
    ax.set_ylabel("Rtransfer/Rcontact", fontsize=20)
    ax2.set_ylabel("Proteins x β/cell", fontsize=20)
    ax.set_ylim(0, 0.1)
    ax2.set_ylim(0, 0.1)

    lns = lineA + lineB
    labs = [x.get_label() for x in lns]
    ax.legend(lns, labs, loc=0, fontsize=20)
    plt.show()

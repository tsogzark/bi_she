import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import os
import math
import sys
import copy
import multiprocessing

def get_tif_map(path):
    tif_names = os.listdir(path)
    tif_index_map = {}
    for tif_name in tif_names:
        if ".tif" in tif_name:
            tif_index = int(list(tif_name.split("-"))[0])
            tif_index_map[tif_index] = tif_name
    return tif_index_map


def process_point(path):
    print("Processing %s" % path)
    fitc_path = path + "FITC/"
    bf_path = path + "BF-1/"
    try:
        os.mkdir(bf_path + "xyAdjust")
    except Exception as e:
        print(e)

    try:
        os.mkdir(fitc_path + "xyAdjust")
    except Exception as e:
        print(e)

    target_path = path + "FITC/xyAdjust/"
    tif_index_map = get_tif_map(fitc_path)
    bf_index_map = get_tif_map(bf_path)
    first_fitc = cv.imread(fitc_path + tif_index_map[0], -1)
    first_bf = cv.imread(bf_path + bf_index_map[0], -1)
    cv.imwrite("%s%s"%(target_path, tif_index_map[0]), first_fitc)
    cv.imwrite("%s%s"%(bf_path + "xyAdjust/", "0.tif"), first_bf)
    for i in range(1, len(bf_index_map)):
        target_img = cv.imread(target_path + tif_index_map[i - 1], -1)
        src_img = cv.imread(fitc_path + tif_index_map[i], -1)
        bf_img = cv.imread(bf_path + bf_index_map[i], -1)
        result = get_offset(src_img, target_img, 100)
        cv.imwrite("%s%s"%(target_path, tif_index_map[i]), result["img"])
        cv.imwrite("%sxyAdjust/%d.tif"%(bf_path, i), gen_offset_img(bf_img, 100, result["dh"], result["dw"]))

def gen_offset_img(img, d, dh, dw):
    h, w = img.shape[:2]
    canvas = np.zeros((h + 2 * d, w + 2 * d), dtype=np.uint16)
    canvas[d:d+h, d:d+w] = img[:,:]
    return canvas[dh:dh+h, dw:dw+w]

def cannyTh(src):
    img = src.astype(np.uint8)
    img = cv.GaussianBlur(img, (3, 3), 0)
    img = cv.Canny(img, 0, 0, apertureSize=7, L2gradient=True)
    empty = np.zeros(img.shape)
    empty[np.where(img == 2**8-1)] = 1
    srcCopy = copy.deepcopy(src)
    srcCopy[np.where(img != 2**8-1)] = 0
    th = np.sum(srcCopy)/np.sum(empty)
    return binary_img(src, th)


def binary_img(img, th):
    th_hold = th
    ret, th_img = cv.threshold(img, th_hold, 2**16 - 1, cv.THRESH_BINARY)
    th_img[np.where(th_img != 2**16 - 1)] = 0
    return th_img


def otus_16bit(img):
    m = img.mean()
 
    hist = cv.calcHist([img],
                        [0],  # 使用的通道
                        None,  # 没有使用mask
                        [65536],  # HistSize
                        [0, 65535])  # 直方图柱的范围
 
    sigma_both = []
    for threshold in range(1, 65536):
        pixel_prob = hist/img.size
        w0_threshold = pixel_prob[:threshold].sum()
        # print("w0_threshold", w0_threshold)
        w1_threshold = 1 - w0_threshold
        # print("w1_threshold", w1_threshold)
        mu0 = hist[:threshold].mean()
        mu1 = hist[threshold:].mean()
        sigma_both.append(w0_threshold*math.pow(mu0 - m, 2) + w1_threshold*math.pow(mu1 - m, 2))
    th_hold = sigma_both.index(max(sigma_both))
    return binary_img(img, th_hold)

def get_offset(src, target, d):
    h, w = src.shape[:2]
    src_otus = cannyTh(src)
    target_otus = cannyTh(target)
    canvas = np.zeros((h + 2 * d, w + 2 * d), dtype=np.uint16)
    canvas_src = np.zeros((h + 2 * d, w + 2 * d), dtype=np.uint16)
    offset_mat = np.zeros((2 * d,  2 * d))
    canvas[d:d+h, d:d+w] = src_otus[:,:]
    canvas_src[d:d+h, d:d+w] = src[:,:]
    for i in range(0, 2 * d, 5):
        for j in range(0, 2 * d, 5):
            delta_mat = canvas[i:i+h, j:j+w] - target_otus
            offset_mat[i,j] = len(np.where(delta_mat == 0)[0])
    max_coor = np.where(offset_mat == np.max(offset_mat))
    dh, dw = max_coor[0][0], max_coor[1][0]
    return {"img":canvas_src[dh:dh+h, dw:dw+w], "dw":dw, "dh":dh}


def process_points(path_list):
    print("In xyAdjust.py thread, Processing:")
    print("<_____---^_^---_____>")
    print(path_list)
    print("<_____---^_^---_____>")
    for path in path_list:
        try:
            process_point(path + "/")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    coreNum = int(sys.argv[2])
    path = "./pointSets/%s/" % sys.argv[1]
    point_dirs = []
    for d in os.listdir(path):
        if "." not in d:
            point_dirs.append(path + d)
    step = int(len(point_dirs)/coreNum) + 1
    path_for_th = []
    div_num = 0
    while div_num * step < len(point_dirs):
        path_for_th.append(point_dirs[div_num * step: min(len(point_dirs), div_num + 1)*step])
        div_num += 1
    threads = []
    for paths in path_for_th:
        tmpTh = multiprocessing.Process(target=process_points, args=(paths, ))
        threads.append(tmpTh)
    for th in threads:
        th.start()

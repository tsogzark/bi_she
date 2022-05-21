from audioop import minmax
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import os

def imagej_hist(src):
    maximum = np.max(src)
    minimum = np.min(src)
    scale_map = np.linspace(minimum, maximum, num=2**8, endpoint=False)
    scale_map = np.append(scale_map, maximum)
    hist = []
    for i in range(2**8):
        up = len(np.where(src>=scale_map[i])[0])
        down = len(np.where(src<scale_map[i+1])[0])
        hist.append(up + down - src.size)
    return hist

def auto_br(src):
    """
    Copy from imageJ
    """ 
    src = src[512:512+1024, 512:512+1024]
    h, w = src.shape[:2]
    src_min = np.min(src)
    src_max = np.max(src)
    src8bit = (src/2**16*2**8).astype(np.uint8)
    src8_min = np.min(src8bit)
    src8_max = np.max(src8bit)
    pixel_count = h * w
    hist = imagej_hist(src)
    th = pixel_count/5000
    limit = pixel_count/10
    bin_size = (src_max - src_min) / 2**8
    hmin = 0
    hmax = 2**8-1
    for i in range(len(hist)):
        count = hist[i]
        count = 0 if count>limit else count
        if count > th:
            hmin = i
            break
    for i in range(len(hist)):
        count = hist[2**8-1 - i]
        count = 0 if count>limit else count
        if count > th:
            hmax = 2**8-1 -i
            break
    tgt_min = src_min + hmin * bin_size
    tgt_max = src_min + hmax * bin_size
    print(tgt_min, tgt_max)
    tgt_img = ((src - tgt_min) * 2**16/(tgt_max - tgt_min))
    tgt_img[np.where(tgt_img <= 0)] = 0
    tgt_img[np.where(tgt_img >= 2**16 - 1)] = 2**16 - 1
    tgt_img = tgt_img.astype(np.uint16)
    return tgt_img

if __name__ == "__main__":
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    DIR = os.path.dirname(__file__) + "/"
    src = cv.imread(DIR + "source.tif", -1)
    tgt = auto_br(src)
    src = src[512:512+1024, 512:512+1024]
    tgt = tgt[512:512+1024, 512:512+1024]
    cv.imwrite(DIR + "src_recut.tif", src)
    src_hist = np.histogram(src, bins=2**16)[0]
    tgt_hist = np.histogram(tgt,bins=2**16)[0]
    print(np.min(src), np.max(src))
    print(np.min(tgt), np.max(tgt))
    fig = plt.figure()
    ax = fig.subplots(1,2)
    ax[0].plot(src_hist/(1024^2))
    ax[0].set_xlabel("灰度")
    ax[0].set_ylabel("频率")
    ax[0].annotate("min:7006\nmax:28972", (0,0), (60000,0.8))
    ax[1].plot(tgt_hist/(1024^2))
    ax[1].set_xlabel("灰度")
    ax[1].set_ylabel("频率")
    ax[1].annotate("min:0\nmax:65535", (0,0), (60000,0.8))
    plt.show()
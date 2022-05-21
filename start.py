import os
import numpy as np
import cv2 as cv

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
    tgt_img = ((src - tgt_min) * 2**16/(tgt_max - tgt_min))
    tgt_img[np.where(tgt_img <= 0)] = 0
    tgt_img[np.where(tgt_img >= 2**16 - 1)] = 2**16 - 1
    tgt_img = tgt_img.astype(np.uint16)
    return tgt_img


if __name__ == "__main__":
    DIR = os.path.dirname(__file__) + "/"
    try:
        os.mkdir(DIR + "xyAdjust/rename")
    except Exception as e:
        print(e)

    dirs = os.listdir(DIR + "xyAdjust")
    for d in dirs:
        if "tif" in d:
            tmpA = cv.imread("%s/xyAdjust/%s" % (DIR,d), -1)
            tmpA = auto_br(tmpA)
            cv.imwrite("%s/xyAdjust/rename/A0A0A%03d.tif" % (DIR,int(list(d.split("."))[0])), tmpA)

    FITCDIR = DIR + "../FITC/xyAdjust/"
    fitc_dirs = os.listdir(FITCDIR)
    try:
        os.mkdir(FITCDIR + "recut/")
    except Exception as e:
        print(e)
    for d in fitc_dirs:
        if "tif" in d:
            tmpB = cv.imread("%s%s"%(FITCDIR, d), -1)
            cv.imwrite("%srecut/%s"%(FITCDIR, d), tmpB[512:512+1024, 512:512+1024])


    os.system('python "/home/tsogzark/git/delta_origin/delta/main.py" "%s"' % (DIR + "xyAdjust/rename"))

import os
import sys
import numpy as np
import pickle
import matplotlib.pyplot as plt
import cv2 as cv

if __name__ == "__main__":
    pkl_path = "E:/delta/autoBR/seg/delta_results/Position000000.pkl"
    with open(pkl_path, "rb") as f:
        pkl = pickle.load(f)
    img = np.array(pkl.rois[0].label_stack[0])
    print(pkl.rois[0].lineage.cells[0])
    cv.imwrite("./autoBR/label_stack.tif", img)
    plt.imshow(img, "gray")
    plt.show()
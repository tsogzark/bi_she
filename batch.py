import sys
import os

def print_gap(s):
    print("")
    print("")
    print(s)
    print("")
    print("")


if __name__ == "__main__":
    coreNum = sys.argv[2]
    day = sys.argv[1]
    print_gap("xyAdjust.py")
    # os.system("python xyAdjust.py %s %s" % (day, coreNum))
    print_gap("move.py")
    # os.system("cp start.py ./pointSets/%s/" % day)
    # os.system("cp move.py ./pointSets/%s/" % day)
    # os.system("cp all.py ./pointSets/%s/" % day)
    # os.system("python ./pointSets/%s/move.py" % day)
    print_gap("all.py")
    # os.system("python ./pointSets/%s/all.py" % day)
    print_gap("longTimeBinary.py")
    os.system("python longTimeBinary.py %s %s" % (day, coreNum))
    print_gap("pklAnalysis.py")
    os.system("python pklAnalysis.py %s %s" % (day, coreNum))

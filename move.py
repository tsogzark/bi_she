import os

if __name__ == "__main__":
    DIR = os.path.dirname(__file__) + "/"
    dirs = os.listdir(DIR)
    for d in dirs:
        if not "." in d:
            os.system("cp \"%sstart.py\" \"%s%s/BF-1/start.py\""%(DIR, DIR, d))

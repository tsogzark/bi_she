import os

DIR = os.path.dirname(__file__) + "/"
for d in os.listdir(DIR):
    if "." not in d:
        os.system("python " + DIR + d + "/BF-1/start.py")

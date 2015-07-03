#import ggplot
#from ggplot import *

def build_data():
    with open("results.txt") as fi:
        data = eval(fi.read())
    for item in data:
        pass



if __name__ == "__main__":
    build_data()
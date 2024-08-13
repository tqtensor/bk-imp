import os

from hyphen import Hyphenator
from hyphen.textwrap2 import fill

# Change to current directory
os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":
    h_en = Hyphenator("en_US")
    appendix = open("appendix.tex", "r").readlines()
    for line in appendix:
        print(fill(line, width=80, use_hyphenator=h_en))

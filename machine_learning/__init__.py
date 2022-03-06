import os
import sys

packageDir = os.path.dirname(os.path.abspath(__file__))
dataDirPath = os.path.join(packageDir, "data")

def allowRootImports():
    sys.path.append(os.path.join(packageDir, ".."))
import sys
import os

def allowRootImports():
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
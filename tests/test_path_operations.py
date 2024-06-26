import sys
import time 
sys.path.append("../scarecro")

import os
whole_path = os.path.abspath(os.getcwd())
print(whole_path)
split_path = whole_path.split("/")
print(split_path)
print(split_path)
print(split_path[0:-2])
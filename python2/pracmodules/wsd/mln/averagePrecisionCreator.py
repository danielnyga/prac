import sys
from utils.eval import ConfusionMatrix
import os
import re
import time

class WritableObject:
    def __init__(self):
        self.content = []
    def write(self, string):
        self.content.append(string)
        
if __name__ == '__main__':
    args = sys.argv[1:]
    path = '.'
    filename = time.strftime("%a_%d_%b_%Y_%H:%M:%S_Compare_Results", time.localtime())
    
    if len(args) == 2:
        path = args[0]
        filename = args[1]
    elif len(args) == 1:
        path = args[0]
    
    pattern = r'^\w{3}_\d{2}_\w{3}_\d{4}_\d{2}:\d{2}:\d{2}_K=\d+_TSC=\d+$'
    gen = (f for f in os.listdir(path) if re.search(pattern, f))
    
    print 'Start compare process...'
    
    writable = WritableObject()                   
    sys.stdout = writable
    for f in gen:
        ConfusionMatrix.compareConfusionMatrices(os.path.join(path,f,'FOL','conf_matrix.cm'),os.path.join(path,f,'FUZZY','conf_matrix.cm'))
    
    sys.stdout = sys.__stdout__    
    
    f = open(filename, 'w')
    for content in writable.content:
        f.write(content)
    f.close()
    print 'done'
    
    

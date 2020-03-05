import numpy as np
import matplotlib.pyplot as plt
import os

with open('decend_log.txt', 'r') as f:
    readlines = f.readlines()
    loss = np.array([0],dtype=np.float32)
    x = np.array([0],dtype=np.float32)
    for i in range(len(readlines)):
        if i == 0:
            loss = float(readlines[i])
            x = 0
        else:
            loss = np.append(loss,float(readlines[i]))
            x = np.append(x,i)
    
    print(loss)
    plt.plot(x,loss)
    plt.show()
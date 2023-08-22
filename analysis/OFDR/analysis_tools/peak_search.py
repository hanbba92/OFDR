from scipy.signal import find_peaks
import numpy as np
import matplotlib.pyplot as plt

def peak_search_smooth(x,y,box_pts):
    y=smooth(y,box_pts)
    return find_peaks(y,distance=100)[0]
    
def smooth(y,box_pts):
    box=np.ones(box_pts)/box_pts
    y_smooth=np.convolve(y,box,mode='same')
    return y_smooth


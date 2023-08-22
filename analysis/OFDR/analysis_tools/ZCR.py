import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import time
from scipy.interpolate import *
from scipy.optimize import curve_fit
from FFT_abs import *


def zero_crossing_resampler3(t,fut,aux,edge):
    t=np.array(t,copy=True)
    fut=np.array(fut,copy=True)
    aux=np.array(aux,copy=True)
    aux_positive_index=np.where(aux>0)[0]
    aux_zci=aux_positive_index[np.where(np.diff(aux_positive_index)>2)[0]]
    t=t[aux_zci]-aux[aux_zci]*(t[aux_zci+1]-t[aux_zci])/(aux[aux_zci+1]-aux[aux_zci])
    fut=fut[aux_zci]
    fut_cubic=CubicSpline(t,fut,bc_type='not-a-knot')
    return t,fut_cubic(t)
    

def signal_filter1(signal):
    signal=np.array(signal,copy=True)
    zero_threshold=1e-3
    signal_sign=np.sign(signal)
    signal_sign_diff1=np.diff(signal_sign)
    signal_sign_diff2=np.diff(signal_sign_diff1)
    signal_sign_diff3=np.diff(signal_sign_diff2)
    signal_sign_diff4=np.diff(signal_sign_diff3)
    signal_sign_diff3_8_index=np.where(abs(signal_sign_diff3)==8)[0]    
    signal[signal_sign_diff3_8_index+1]=(2*signal[signal_sign_diff3_8_index]+signal[signal_sign_diff3_8_index+3])/3
    signal[signal_sign_diff3_8_index+2]=(signal[signal_sign_diff3_8_index]+2*signal[signal_sign_diff3_8_index+3])/3
    signal_sign_diff4_12_index=np.where(abs(signal_sign_diff4)==12)[0]
    signal[signal_sign_diff4_12_index]=(3*signal[signal_sign_diff4_12_index-1]+signal[signal_sign_diff4_12_index+3])/4
    signal[signal_sign_diff4_12_index+1]=(signal[signal_sign_diff4_12_index-1]+signal[signal_sign_diff4_12_index+3])/2
    signal[signal_sign_diff4_12_index+2]=(signal[signal_sign_diff4_12_index-1]+3*signal[signal_sign_diff4_12_index+3])/4
    return signal

def rejection_filter_of_linear_component(t,y):
    popt,pcov=curve_fit(linear_func,t,y)
    return y-linear_func(t,*popt)

def linear_func(x,a,b):
    return a*x+b





        


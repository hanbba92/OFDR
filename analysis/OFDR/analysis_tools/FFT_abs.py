import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import time

def fft_abs(signal,sampling_period):
    signal_fft=np.fft.fft(signal)
    signal_fft_0=abs(signal_fft)*(2/len(signal_fft))
    f=np.fft.fftfreq(len(signal_fft),sampling_period)
    data_length=int(len(f)/2)
    return f[0:data_length],signal_fft_0[0:data_length]

def sp_fft_abs(signal,sampling_period):
    signal_fft=sp.fft.fft(signal)
    signal_fft_0=abs(signal_fft)*(2/len(signal_fft))
    f=sp.fft.fftfreq(len(signal_fft),sampling_period)
    data_length=int(len(f)/2)
    return f[0:data_length],signal_fft_0[0:data_length]

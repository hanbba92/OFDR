import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
f0="C:/OFDR_DATA/M0003701/2023_10_06_13.32.31_-40.0.npy"
f1="C:/OFDR_DATA/M0003701/2023_10_06_14.02.23_-30.0.npy"
f2="C:/OFDR_DATA/M0003701/2023_10_06_15.22.35_-10.0.npy"
f3="C:/OFDR_DATA/M0003701/2023_10_06_16.30.24_0.0.npy"
f4="C:/OFDR_DATA/M0003701/2023_10_06_16.57.44_15.0.npy"
f5="C:/OFDR_DATA/M0003701/2023_10_06_17.32.34_30.0.npy"

d0=np.load(f0)
d1=np.load(f1)
d2=np.load(f2)
d3=np.load(f3)
d4=np.load(f4)
d5=np.load(f5)

fig,ax =plt.subplots(figsize=(15,20))
y_major_ticks=np.arange(-180,-40,10)
y_minor_ticks=np.arange(-180,-40,5)
x_major_ticks=np.arange(0,5000,500)
x_minor_ticks=np.arange(0,5000,100)

ax.plot(d0[0],d0[1],label='-40\'C')
ax.plot(d1[0],d1[1],label='-30\'C')
ax.plot(d2[0],d2[1],label='-10\'C')
ax.plot(d3[0],d3[1],label='0\'C')
ax.plot(d4[0],d4[1],label='15\'C')
ax.plot(d5[0],d5[1],label='30\'C')


ax.set_xticks(x_major_ticks)
ax.set_xticks(x_minor_ticks,minor=True)
ax.set_yticks(y_major_ticks)
ax.set_yticks(y_minor_ticks, minor=True)
ax.grid(which='minor', alpha=0.5)
ax.grid(which='major', alpha=0.9)
plt.xlabel('Distance (mm)')
plt.ylabel('Reflection Coefficient (dB)')
plt.legend()
plt.suptitle('M0003701 RC vs Temp', size=20)
plt.show()

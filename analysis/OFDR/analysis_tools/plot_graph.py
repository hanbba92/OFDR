import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

f1='C:/OFDR_DATA/30_temp_four_dut/M0003709.npy'
f2='C:/OFDR_DATA/30_temp_four_dut/M0003991.npy'
f3='C:/OFDR_DATA/30_temp_four_dut/M0003999.npy'
f4='C:/OFDR_DATA/30_temp_four_dut/M0003701.npy'

d1=np.load(f1)
print(d1)
d2=np.load(f2)
d3=np.load(f3)
d4=np.load(f4)

fig,ax =plt.subplots(figsize=(15,20))
y_major_ticks=np.arange(-180,-40,10)
y_minor_ticks=np.arange(-180,-40,5)
x_major_ticks=np.arange(0,5000,500)
x_minor_ticks=np.arange(0,5000,100)

ax.plot(d1[0],d1[1],label='M0003709')
ax.plot(d2[0],d2[1],label='M0003991')
ax.plot(d3[0],d3[1],label='M0003999')
ax.plot(d4[0],d4[1],label='M0003701')
ax.set_xticks(x_major_ticks)
ax.set_xticks(x_minor_ticks,minor=True)
ax.set_yticks(y_major_ticks)
ax.set_yticks(y_minor_ticks, minor=True)
ax.grid(which='minor', alpha=0.5)
ax.grid(which='major', alpha=0.9)
plt.xlabel("Distance (mm)")
plt.ylabel("Reflection Coefficient (dB)")
plt.legend()
plt.suptitle('4-DUT 30 Degree Celcius Comparison', size=20)
plt.show()

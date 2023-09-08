import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


def find_nearest_value_index(arr,value):
    difference_array=np.absolute(arr-value)
    index = difference_array.argmin()
    return index

def FIND_PEAKS(RC,threshold, Distance, Input_Start, Input_End, Output_Start, Output_End):

    input_start=find_nearest_value_index(Distance,Input_Start)
    input_end=find_nearest_value_index(Distance,Input_End)
    output_start=find_nearest_value_index(Distance,Output_Start)
    output_end=find_nearest_value_index(Distance, Output_End)

    Input_RC=RC[input_start:input_end+1]
    Output_RC=RC[output_start:output_end+1]
    Input_Peaks_ind,_=find_peaks(Input_RC,height=threshold)
    Output_Peaks_ind,_=find_peaks(Output_RC,height=threshold)

    Input_Peak_Values=[]
    Output_Peak_Values=[]
    for ind in Input_Peaks_ind:
        Input_Peak_Values.append((Distance[input_start+ind],Input_RC[ind]))
    for ind in Output_Peaks_ind:
        Output_Peak_Values.append((Distance[output_start+ind],Output_RC[ind]))


    return Input_Peak_Values, Output_Peak_Values

def Collect_Peak_Data(bins,count,folder_path,file_list,Input_Start,Input_End,Output_Start,Output_End,threshold):
    Peak_Data=[[],[]]
    for i in bins:
        filename_list=file_list[count*(i-1):(i*count)]
        input_peaks=[]
        output_peaks=[]
        for filename in filename_list:
            data=np.load(folder_path+'/'+filename)
            RC=data[1]
            Distance=data[0]
            input_pks,output_pks=FIND_PEAKS(RC,threshold,Distance,Input_Start,Input_End,Output_Start,Output_End)
            input_peaks.append(input_pks)
            output_peaks.append(output_pks)
        Peak_Data[0].append(input_peaks)
        Peak_Data[1].append(output_peaks)
    return Peak_Data

def Find_Average(Data,Data_type):
    Input_average = []

    for hourly_data in Data[Data_type]:
        hour_max = []
        for ten_min_data in hourly_data:
            peak_val = []
            for peak_data in ten_min_data:
                distance = peak_data[0]
                peak_val.append(peak_data[1])
            max_peak = max(peak_val)
            hour_max.append(max_peak)
        Input_average.append(np.average(hour_max))
    return Input_average


bins=[1,2,3,4,5,6,7,8,9,10,11,12]
folder_path_M0003701='C:/OFDR_DATA/M0003701_Chamber'
file_list=os.listdir(folder_path_M0003701)

Input_Start=2546.039
Input_End=2566.79
Output_Start = 2566.79
Output_End = 2583.17
threshold=-92.5
count=6

Peak_Data_M0003701= Collect_Peak_Data(bins,count,folder_path_M0003701,file_list,Input_Start,Input_End,Output_Start,Output_End,threshold)
Average_Input_Data_M0003701=Find_Average(Peak_Data_M0003701,0)


plt.subplot(311)
plt.plot(bins,Average_Input_Data_M0003701)
plt.xticks(bins)
plt.xlabel("Time (h)")
plt.ylabel("Reflection Coefficient (dB)")
plt.title("M0003701_1")



bins=[1,2,3,4,5,6]
folder_path_M0003709='C:/OFDR_DATA/M0003709_Chamber'
file_list=os.listdir(folder_path_M0003709)
Peak_Data=[[],[]]

Input_Start=3185
Input_End=3204
Output_Start = 3204
Output_End = 3221
threshold=-95
count=10

Peak_Data_M0003709= Collect_Peak_Data(bins,count,folder_path_M0003709,file_list,Input_Start,Input_End,Output_Start,Output_End,threshold)
Average_Input_Data_M0003709=Find_Average(Peak_Data_M0003709,0)



temp=[-40,-30,-15,0,15,30]
plt.subplot(312)
plt.plot(temp,Average_Input_Data_M0003709[::-1])
plt.xticks(temp)
plt.xlabel("Temperature ('C)")
plt.ylabel("Reflection Coefficient (dB)")
plt.title("M0003709")





bins=[1,2,3,4]
folder_path_M0003991='C:/Users/FIBERPRO_OMEGA/Desktop/CHAMBER_M0003991'
file_list=os.listdir(folder_path_M0003991)
Peak_Data=[[],[]]

Input_Start=2533
Input_End=2568
Output_Start = 2568
Output_End = 2583
threshold=-92
count=10

Peak_Data_M0003991= Collect_Peak_Data(bins,count,folder_path_M0003991,file_list,Input_Start,Input_End,Output_Start,Output_End,threshold)
Average_Input_Data_M0003991=Find_Average(Peak_Data_M0003991,0)


temp=[-40,-30,-15,0]
plt.subplot(313)
plt.plot(temp,Average_Input_Data_M0003991[::-1])
plt.xticks(temp)
plt.xlabel("Temperature ('C)")
plt.ylabel("Reflection Coefficient (dB)")
plt.title("M0003701_2")
plt.tight_layout()
plt.show()

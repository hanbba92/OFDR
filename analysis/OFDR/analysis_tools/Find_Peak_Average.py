import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


def find_nearest_value_index(arr,value):
    difference_array=np.absolute(arr-value)
    index = difference_array.argmin()
    return index

def FIND_IN_OUT_PEAKS(RC,threshold, Distance, Input_Start, Input_End, Output_Start, Output_End):

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

def FIND_SINGLE_PEAK(RC,threshold, Distance, Start, End):

    start = find_nearest_value_index(Distance, Start)
    end = find_nearest_value_index(Distance, End)


    RC_Data = RC[start:end + 1]

    Peak_ind, _ = find_peaks(RC_Data, height=threshold)


    Peak_Value = []
    if len(Peak_ind)==0:
        Peak_Value.append((0,threshold-1))
    else:
        for ind in Peak_ind:
            Peak_Value.append((Distance[start + ind], RC_Data[ind]))

    Dummy_Value=[]
    return Peak_Value, Dummy_Value

def Collect_Peak_Data(bins,count,folder_path,file_list,Input_Start,Input_End,Output_Start,Output_End,threshold,position=0):
    Peak_Data=[[],[]]
    for i in bins:
        filename_list=file_list[count*(i-1):(i*count)]
        input_peaks=[]
        output_peaks=[]
        for filename in filename_list:
            data=np.load(folder_path+'/'+filename)
            RC=data[1]
            Distance=data[0]
            if position == 0:
                input_pks,output_pks=FIND_IN_OUT_PEAKS(RC,threshold,Distance,Input_Start,Input_End,Output_Start,Output_End)
                input_peaks.append(input_pks)
                output_peaks.append(output_pks)
            else:
                single_pks, _ = FIND_SINGLE_PEAK(RC,threshold,Distance,Input_Start,Input_End)
                input_peaks.append(single_pks)
                output_peaks.append([])
        Peak_Data[0].append(input_peaks)
        Peak_Data[1].append(output_peaks)

    return Peak_Data

def Find_Average(Data,Data_type,threshold):
    Temp_average = []

    for temp_data in Data[Data_type]:
        temp_max = []
        for repeated_data in temp_data:
            peak_val = []
            for peak_data in repeated_data:


                distance = peak_data[0]
                peak_val.append(peak_data[1])
            max_peak = max(peak_val)
            temp_max.append(max_peak)
        Temp_average.append(np.average(temp_max))
    return Temp_average


# bins=[1,2,3,4,5,6,7,8,9,10,11,12]
# folder_path_M0003701='C:/OFDR_DATA/M0003701_Chamber_switch_off_from_minus_40'
# file_list=os.listdir(folder_path_M0003701)
#
# Input_Start=2546.039
# Input_End=2566.79
# Output_Start = 2566.79
# Output_End = 2583.17
# threshold=-92.5
# count=6
#
# Peak_Data_M0003701= Collect_Peak_Data(bins,count,folder_path_M0003701,file_list,Input_Start,Input_End,Output_Start,Output_End,threshold)
# Average_Input_Data_M0003701=Find_Average(Peak_Data_M0003701,1)
#
#
# plt.plot(bins,Average_Input_Data_M0003701, label='M0003701')
# plt.xlabel("Time (h)")
# #plt.title("M0003701")
#
#
#
# bins=[1,2,3,4,5,6,7,8,9,10,11,12]
# folder_path_M0003709='C:/OFDR_DATA/M0003709_Chamber_switch_off_from_minus_40'
# file_list=os.listdir(folder_path_M0003709)
# Peak_Data=[[],[]]
#
# Input_Start=3185
# Input_End=3204
# Output_Start = 3204
# Output_End = 3219
# threshold=-95
# count=6
#
# Peak_Data_M0003709= Collect_Peak_Data(bins,count,folder_path_M0003709,file_list,Input_Start,Input_End,Output_Start,Output_End,threshold)
# Average_Input_Data_M0003709=Find_Average(Peak_Data_M0003709,1)
#
#
#
# temp=[-40,-30,-15,0,15,30]
#
# plt.plot(bins,Average_Input_Data_M0003709[::-1], label='M0003709')
# plt.xticks(bins)
#
#
# plt.title("M0003701 vs M0003709")

bins=[1,2,3,4,5,6]
temp=[-40,-30,-15,0,15,30]


# M0003709


folder_path='C:\OFDR_DATA/M0003709'
file_list=os.listdir(folder_path)
Peak_Data=[[],[]]

Input_Start=3183
Input_End=3201
Output_Start = 3201
Output_End = 3219
threshold_1=-92
count=10

Peak_Data= Collect_Peak_Data(bins,count,folder_path,file_list,Input_Start,Input_End,Output_Start,Output_End,threshold_1,0)

Average_Input_Data=Find_Average(Peak_Data,0,threshold_1)

Average_Output_Data=Find_Average(Peak_Data,1,threshold_1)

Single_Start = 3220
Single_End = 3226
threshold_2 = -100

Single_Peak_Data= Collect_Peak_Data(bins,count,folder_path,file_list,Single_Start,Single_End,Output_Start,Output_End,threshold_2,1)

Single_Average_Input_Data=Find_Average(Single_Peak_Data,0,threshold_2)

plt.subplot(311)
plt.title("Input RC vs Temp")
plt.plot(temp,Average_Input_Data, label='M0003709')
plt.legend()
plt.xlabel("Temperature ('C)")
plt.ylabel("Reflection Coefficient (dB)")
print("M0003709 Input")
print("Average: ", np.average(Average_Input_Data)," Var: ", np.var(Average_Input_Data), " Stdev: ", np.std(Average_Input_Data))
print(Average_Input_Data)
print()

plt.subplot(312)
plt.title("Output RC vs Temp")
plt.plot(temp,Average_Output_Data,label='M0003709')
print("M0003709 Output")
print("Average: ", np.average(Average_Output_Data)," Var: ", np.var(Average_Output_Data), " Stdev: ", np.std(Average_Output_Data))
print(Average_Output_Data)
print()
plt.xlabel("Temperature ('C)")
plt.ylabel("Reflection Coefficient (dB)")
plt.legend()

plt.subplot(313)
plt.title("6~7mm from Output RC vs Temp")
plt.plot(temp,Single_Average_Input_Data,label='M0003709')
print("M0003709 Single")
print("Average: ", np.average(Single_Average_Input_Data)," Var: ", np.var(Single_Average_Input_Data), " Stdev: ", np.std(Single_Average_Input_Data))
print(Single_Average_Input_Data)
print()
plt.xlabel("Temperature ('C)")
plt.ylabel("Reflection Coefficient (dB)")
plt.legend()



# #M0003701
#
# folder_path = 'C:/Users/FIBERPRO_OMEGA/Desktop/M0003701'
# file_list=os.listdir(folder_path)
# Peak_Data=[[],[]]
#
# Input_Start=2533
# Input_End=2568
# Output_Start = 2568
# Output_End = 2583
# threshold=-92
# count=10
#
# Peak_Data= Collect_Peak_Data(bins,count,folder_path,file_list,Input_Start,Input_End,Output_Start,Output_End,threshold,0)
# Average_Input_Data=Find_Average(Peak_Data,0)
#
# Single_Start = 0
# Single_End = 0
# threshold = 0
#
# Single_Peak_Data= Collect_Peak_Data(bins,count,folder_path,file_list,Single_Start,Single_End,Output_Start,Output_End,threshold,1)
# Single_Average_Input_Data=Find_Average(Single_Peak_Data,0)
#
# plt.subplot(311)
# plt.plot(temp,Average_Input_Data,label='M0003701')
# print("M0003701 Input")
# print("Average: ", np.average(Average_Input_Data)," Var: ", np.var(Average_Input_Data), " Stdev: ", np.std(Average_Input_Data))
# print(Average_Input_Data)
# print()
# Average_Output_Data=Find_Average(Peak_Data,1)
# plt.subplot(312)
# plt.plot(temp,Average_Input_Data,label='M0003701')
# print("M0003701 Output")
# print("Average: ", np.average(Average_Output_Data)," Var: ", np.var(Average_Output_Data), " Stdev: ", np.std(Average_Output_Data))
# print(Average_Output_Data)
# print()
# plt.subplot(313)
# plt.plot(temp,Single_Average_Input_Data,label='M0003701')
# print("M0003701 Single")
# print("Average: ", np.average(Single_Average_Input_Data)," Var: ", np.var(Single_Average_Input_Data), " Stdev: ", np.std(Single_Average_Input_Data))
# print(Single_Average_Input_Data)
# print()
# #M0003991
#
# folder_path = 'C:/Users/FIBERPRO_OMEGA/Desktop/M0003991'
# file_list=os.listdir(folder_path)
# Peak_Data=[[],[]]
#
# Input_Start=2533
# Input_End=2568
# Output_Start = 2568
# Output_End = 2583
# threshold=-92
# count=10
#
# Peak_Data= Collect_Peak_Data(bins,count,folder_path,file_list,Input_Start,Input_End,Output_Start,Output_End,threshold,0)
# Average_Input_Data=Find_Average(Peak_Data,0)
#
# Single_Start = 0
# Single_End = 0
# threshold = 0
#
# Single_Peak_Data= Collect_Peak_Data(bins,count,folder_path,file_list,Single_Start,Single_End,Output_Start,Output_End,threshold,1)
# Single_Average_Input_Data=Find_Average(Single_Peak_Data,0)
#
# plt.subplot(311)
# plt.plot(temp,Average_Input_Data,label='M0003991')
# print("M0003991 Input")
# print("Average: ", np.average(Average_Input_Data)," Var: ", np.var(Average_Input_Data), " Stdev: ", np.std(Average_Input_Data))
# print(Average_Input_Data)
# print()
# Average_Output_Data=Find_Average(Peak_Data,1)
# plt.subplot(312)
# plt.plot(temp,Average_Input_Data,label='M0003991')
# print("M0003991 Output")
# print("Average: ", np.average(Average_Output_Data)," Var: ", np.var(Average_Output_Data), " Stdev: ", np.std(Average_Output_Data))
# print(Average_Output_Data)
# print()
# plt.subplot(313)
# plt.plot(temp,Single_Average_Input_Data,label='M0003991')
# print("M0003701 Single")
# print("Average: ", np.average(Single_Average_Input_Data)," Var: ", np.var(Single_Average_Input_Data), " Stdev: ", np.std(Single_Average_Input_Data))
# print(Single_Average_Input_Data)
# print()
#
# #M0003999
#
# folder_path = 'C:/Users/FIBERPRO_OMEGA/Desktop/M0003999'
# file_list=os.listdir(folder_path)
# Peak_Data=[[],[]]
#
# Input_Start=2533
# Input_End=2568
# Output_Start = 2568
# Output_End = 2583
# threshold=-92
# count=10
#
# Peak_Data= Collect_Peak_Data(bins,count,folder_path,file_list,Input_Start,Input_End,Output_Start,Output_End,threshold,0)
# Average_Input_Data=Find_Average(Peak_Data,0)
#
# Single_Start = 0
# Single_End = 0
# threshold = 0
#
# Single_Peak_Data= Collect_Peak_Data(bins,count,folder_path,file_list,Single_Start,Single_End,Output_Start,Output_End,threshold,1)
# Single_Average_Input_Data=Find_Average(Single_Peak_Data,0)
#
# plt.subplot(311)
# plt.plot(temp,Average_Input_Data,label='M0003999')
# print("M0003999 Input")
# print("Average: ", np.average(Average_Input_Data)," Var: ", np.var(Average_Input_Data), " Stdev: ", np.std(Average_Input_Data))
# print(Average_Input_Data)
# print()
#
# Average_Output_Data=Find_Average(Peak_Data,1)
# plt.subplot(312)
# plt.plot(temp,Average_Input_Data,label='M0003999')
# print("M0003999 Output")
# print("Average: ", np.average(Average_Output_Data)," Var: ", np.var(Average_Output_Data), " Stdev: ", np.std(Average_Output_Data))
# print(Average_Output_Data)
# print()
#
# plt.subplot(313)
# plt.plot(temp,Single_Average_Input_Data,label='M0003999')
# print("M0003999 Single")
# print("Average: ", np.average(Single_Average_Input_Data)," Var: ", np.var(Single_Average_Input_Data), " Stdev: ", np.std(Single_Average_Input_Data))
# print(Single_Average_Input_Data)
# print()






plt.tight_layout()
plt.show()

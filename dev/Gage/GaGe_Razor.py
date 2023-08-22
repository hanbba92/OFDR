from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import pyqtgraph as pg
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os,sys,configparser,webbrowser,time,json
import GageSupport as gs
import GageConstants as gc
import PyGage3_64 as PyGage

class Razor_express():
    def __init__(self):
        try:
            self.handle=self.initialize()
            if self.handle<0:
                print("Error:",PyGage.GetErrorString(self.handle))
                raise
            self.system_info=PyGage.GetSystemInfo(self.handle)
            if not isinstance(self.system_info, dict):
                print("Error: ",PyGage.GetErrorString(self.system_info))
                raise
            print("\nBoard Name: ",self.system_info["BoardName"])
        except:
            PyGage.FreeSystem(self.handle)
            print("Exit initialization")

    def initialize(self):
        status=PyGage.Initialize()
        if status<0:
            return status
        else:
            handle=PyGage.GetSystem(0,0,0,0)
            return handle

    def single_acquisition(self,inst,acq,chan,trig,app):
        PyGage.SetAcquisitionConfig(inst.handle,acq)
        system_info=PyGage.GetSystemInfo(inst.handle)
        channel_increment=gs.CalculateChannelIndexIncrement(acq['Mode'],system_info['ChannelCount'],system_info['BoardCount'])
        self.chan_list=['ch%i'%i for i in range(1,system_info['ChannelCount']+1,channel_increment)]
        for i,chan_id in enumerate(self.chan_list):
            PyGage.SetChannelConfig(inst.handle,1+i*channel_increment,chan[chan_id])
        trigger_count=1
        for i in range(1,trigger_count+1):
            PyGage.SetTriggerConfig(inst.handle,i,trig)
        status=PyGage.Commit(inst.handle)
        if status < 0:
            return status
        status=PyGage.StartCapture(inst.handle)
        if status < 0:
            return status
        capture_time=0
        status=PyGage.GetStatus(inst.handle)
        while status!=gc.ACQ_STATUS_READY:
            status=PyGage.GetStatus(inst.handle)
            if status==gc.ACQ_STATUS_TRIGGERED:
                capture_time=datetime.now().time() 
        if capture_time==0: 
            capture_time=datetime.now().time()
        min_start_address=acq['TriggerDelay']+acq['Depth']-acq['SegmentSize']
        if app['StartPosition']<min_start_address:
            print("\nInvalid Start Address was changed from {0} to {1}".format(app['StartPosition'],min_start_address))
            app['StartPosition']=min_start_address
        max_length=acq['TriggerDelay']+acq['Depth']-min_start_address
        if app['TransferLength']>max_length:
            print("\nInvalid Transfer Length was changed from {0} to {1}".format(app['TransferLength'],max_length))
            app['TransferLength']=max_length
        self.stHeader={}
        self.stHeader['Common']={'Start':app['StartPosition'],
                                 'Length':app['TransferLength'],
                                 'SampleSize':acq['SampleSize'],
                                 'SampleOffset':acq['SampleOffset'],
                                 'SampleRes':acq['SampleResolution'],
                                 'SegmentNumber':1,
                                 'SampleBits':acq['SampleBits'],
                                 'SegmentCount':acq['SegmentCount'],
                                 'SampleRate':acq['SampleRate']/acq['ExtClockSampleSkip']*1000 if acq['ExternalClock'] else acq['SampleRate']}
        self.data=np.zeros((len(self.chan_list),app['TransferLength']),dtype=np.int16)
        for i,chan_id in enumerate(self.chan_list):
            buffer=PyGage.TransferData(inst.handle,1+i*channel_increment,0,1,app['StartPosition'],app['TransferLength'])
            if isinstance(buffer,int):
                print("Error transferring channel ",i)
                return buffer
            self.stHeader[chan_id]={'InputRange':chan[chan_id]['InputRange'],
                                    'DcOffset':chan[chan_id]['DcOffset'],
                                    'Length':buffer[2],
                                    'TimeStamp':{'Hour':capture_time.hour,
                                                 'Minute':capture_time.minute,
                                                 'Second':capture_time.second,
                                                 'Point1Second':capture_time.microsecond//1000}}   
            self.data[i]=buffer[0]
        return self.data,self.stHeader

    def data_int16_to_float64(self):
        self.data_float64=self.data.astype(np.float64)
        for i,chan_id in enumerate(self.chan_list):
            scale_factor=self.stHeader[chan_id]['InputRange']/2000
            offset=self.stHeader[chan_id]['DcOffset']/1000
            self.data_float64[i]=(self.stHeader['Common']['SampleOffset']-self.data[i])/self.stHeader['Common']['SampleRes']*scale_factor+offset
        return self.data_float64

class WorkerSignals(QObject):
    finished=pyqtSignal()
    error=pyqtSignal(tuple)
    result=pyqtSignal(object)
    progress=pyqtSignal(str)

class Work_single_Gage(QRunnable):
    def __init__(self,inst,settings,data_type):
        super().__init__()
        self.inst=inst
        self.settings_dict=settings
        self.data_type=data_type
        self.signals=WorkerSignals()

    def run(self):
        acq=self.DictAcquisitionConfiguration(self.inst.handle)
        chan=self.DictChannelConfiguration(self.inst.handle)
        trig=self.DictTriggerConfiguration(self.inst.handle,1)
        app=self.DictApplicationConfiguration()
        self.inst.single_acquisition(self.inst,acq,chan,trig,app)
        if self.data_type=='ascii':
            self.inst.data_int16_to_float64()
        output={'bin':(self.inst.data,self.inst.stHeader),'ascii':(getattr(self.inst,'data_float64','data'),self.inst.stHeader)}.get(self.data_type)
        self.signals.result.emit(output)
        self.signals.finished.emit()

    def DictAcquisitionConfiguration(self,handle):
        acq=PyGage.GetAcquisitionConfig(handle)
        unit_dict={'k':1000,'M':1000000}
        acq['Mode']=int(self.settings_dict['Acquisition']['Mode']) if 'Mode' in self.settings_dict['Acquisition'] else 1
        acq['SampleRate']=int(self.settings_dict['Acquisition']['SampleRate'][:-5])*int(unit_dict[self.settings_dict['Acquisition']['SampleRate'][-4]])
        acq['SampleBits']=int(16)
        acq['SampleResolution']=int(-32768)
        acq['SampleSize']=int(2)
        acq['SampleOffset']=-1
        acq['TimeStampConfig']=0
        acq['Depth']=1000*int(self.settings_dict['Acquisition']['Depth']) if 'Depth' in self.settings_dict['Acquisition'] else 8160
        acq['SegmentSize']=1000*int(self.settings_dict['Acquisition']['SegmentSize']) if 'SegmentSize' in self.settings_dict['Acquisition'] else 8160
        acq['SegmentCount']=int(self.settings_dict['Acquisition']['SegmentCount']) if 'SegmentCount' in self.settings_dict['Acquisition'] else 1
        acq['TriggerHoldoff']=int(self.settings_dict['Acquisition']['TriggerHoldoff']) if 'TriggerHoldoff' in self.settings_dict['Acquisition'] else 0
        acq['TriggerTimeout']=int(self.settings_dict['Acquisition']['TriggerTimeout']) if 'TriggerTimeout' in self.settings_dict['Acquisition'] else 10000000
        acq['TriggerDelay']=int(self.settings_dict['Acquisition']['TriggerDelay']) if 'TriggerDelay' in self.settings_dict['Acquisition'] else 0
        acq['ExternalClock']=int(self.settings_dict['Acquisition']['ExternalClock']) if 'ExternalClock' in self.settings_dict['Acquisition'] else 0
        if 'ExtClockSampleSkip' in self.settings_dict['Acquisition']: acq['ExtClockSampleSkip']=int(self.settings_dict['Acquisition']['ExtClockSampleSkip'])
        if 'TimeStampClock' in self.settings_dict['Acquisition']:
            if self.settings_dict['Acquisition']['TimeStampClock']=='fixed':
                acq['TimeStampClock']|=gc.TIMESTAMP_MCLK
            else:
                acq['TimeStampClock']&=~gc.TIMESTAMP_MCLK
        if 'TimeStampMode' in self.settings_dict['Acquisition']:
            if self.settings_dict['Acquisition']['TimeStampMode']=='free':
                acq['TimeStampMode']|=gc.TIMESTAMP_FREERUN
            else:
                acq['TimeStampMode']&=~gc.TIMESTAMP_FREERUN
        return acq

    def DictChannelConfiguration(self,handle):
        chan_dict={'ch1':{},'ch2':{},'ch3':{},'ch4':{}}
        for key in chan_dict.keys():
            chan_num=int(key[-1])
            chan_id='Channel'+str(chan_num)
            chan=PyGage.GetChannelConfig(handle,chan_num)
            chan['InputRange']=int(self.settings_dict[chan_id]['InputRange']) if 'InputRange' in self.settings_dict[chan_id] else 2000
            if 'Coupling' in self.settings_dict[chan_id]:
                if self.settings_dict[chan_id]['Coupling']=='DC' or self.settings_dict[chan_id]=='1':
                    chan['Coupling']=gc.CS_COUPLING_DC
                elif self.settings_dict[chan_id]=='AC' or self.settings_dict[chan_id]=='2':
                    chan['Coupling']=gc.CS_COUPLING_AC
            else:
                chan['Coupling']['Coupling']=gc.CS_COUPLING_DC
            chan['Impedance']=int(self.settings_dict[chan_id]['Impedance']) if 'Impedance' in self.settings_dict[chan_id] else 50
            chan['DcOffset']=int(self.settings_dict[chan_id]['DcOffset']) if 'DcOffset' in self.settings_dict[chan_id] else 0
            if 'Filter' in self.settings_dict[chan_id]: chan['Filter']=int(self.settings_dict[chan_id]['Filter'])
            chan_dict[key]=chan
        return chan_dict

    def DictTriggerConfiguration(self,handle,trigger):
        trig=PyGage.GetTriggerConfig(handle,trigger)
        trig_id='Trigger'+str(trigger)
        if 'Condition' in self.settings_dict[trig_id]:
            if self.settings_dict[trig_id]['Condition'] in ['falling', 'negative', '0']:
                trig['Condition'] = gc.CS_TRIG_COND_NEG_SLOPE
            elif self.settings_dict[trig_id]['Condition'] == 'pulsewidth':
                trig['Condition'] = gc.CS_TRIG_COND_PULSE_WIDTH
            else:
                trig['Condition'] = gc.CS_TRIG_COND_POS_SLOPE
        trig['Level']=int(self.settings_dict[trig_id]['Level']) if 'Level' in self.settings_dict[trig_id] else 50
        if 'Source' in self.settings_dict[trig_id]:
            if self.settings_dict[trig_id]['Source'] == 'External':
                trig['Source'] = gc.CS_TRIG_SOURCE_EXT
            elif self.settings_dict[trig_id]['Source'] == 'Disable':
                trig['Source'] = gc.CS_TRIG_SOURCE_DISABLE
            else:					
                trig['Source'] = int(self.settings_dict[trig_id]['Source'])
        if 'ExtCoupling' in self.settings_dict[trig_id]:
            if self.settings_dict[trig_id]['ExtCoupling'] == 'AC':
                trig['ExtCoupling'] = gc.CS_COUPLING_AC
            elif self.settings_dict[trig_id]['ExtCoupling'] == 'DC':
                trig['ExtCoupling'] = gc.CS_COUPLING_DC
            else:
                trig['ExtCoupling'] = int(self.settings_dict[trig_id]['ExtCoupling'])
        trig['ExtRange']=int(self.settings_dict[trig_id]['ExtRange']) if 'ExtRange' in self.settings_dict[trig_id] else 2000
        trig['ExtImpedance']=int(self.settings_dict[trig_id]['ExtImpedance']) if 'ExtImpedance' in self.settings_dict[trig_id] else 50
        if 'Relation' in self.settings_dict[trig_id]: trig['Relation']=int(self.settings_dict[trig_id]['Relation']) 
        return trig

    def DictApplicationConfiguration(self):
        app = {}
        app['StartPosition']=1000*int(self.settings_dict['Application']['StartPosition']) if 'StartPosition' in self.settings_dict['Application'] else 0
        app['TransferLength']=1000*int(self.settings_dict['Application']['TransferLength']) if 'TransferLength' in self.settings_dict['Application'] else 4096
        app['SegmentStart']=int(self.settings_dict['Acquisition']['SegmentStart']) if 'SegmentStart' in self.settings_dict['Acquisition'] else 1
        app['SegmentCount']=int(self.settings_dict['Acquisition']['SegmentCount']) if 'SegmentCount' in self.settings_dict['Acquisition'] else 1
        app['PageSize']=int(self.settings_dict['Application']['PageSize']) if 'PageSize' in self.settings_dict['Application'] else 32768
        return app

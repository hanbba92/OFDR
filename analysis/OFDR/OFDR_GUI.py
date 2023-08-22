from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import pyqtgraph as pg
import time,sys,traceback,os,json,configparser
import numpy as np
import scipy as sp
import pandas as pd
from scipy.signal import find_peaks
from analysis_tools import *
sys.path.append('../..')
from dev import *
import icon_rc

form_class_Analysis_OFDR = uic.loadUiType('C:\\GUI\\analysis\\OFDR\\OFDR.ui')[0]
class Analysis_OFDR_Window(QMainWindow,form_class_Analysis_OFDR):
    def __init__(self,*args,**kwargs):
        self.threadpool=QThreadPool()
        super(QMainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.show()
        self.threadpool=QThreadPool()
        self.plot_initialize()
        self.init_connection()
        self.measuring=False

    def init_connection(self):
        if 'tel' in dir(self):
            self.Connection_TLS_8164A_w=Connection_TLS_8164A_Window(tel=self.tel)
        else:
            self.Connection_TLS_8164A_w=Connection_TLS_8164A_Window()
        self.Connection_TLS_8164A_w.to_main_signals.result.connect(self.receive_tel)
        self.Connection_TLS_8164A_w.show()
        self.inst_Gage=Razor_express()

    def plot_initialize(self):
        self.OFDR_plot.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        self.OFDR_plot.plotItem.setLabels(left='Reflection coefficient',bottom='Distance (mm)')
        self.OFDR_plot.setXRange(0,5000)
        if self.LogscalecheckBox.isChecked():
            self.OFDR_plot.setYRange(-140,-20)
        else:
            self.OFDR_plot.setYRange(0,100)
        self.OFDR_plot.showGrid(x = True, y = True, alpha = 0.77)     
        self.OFDR_plot.enableAutoRange('xy', False)
        self.plt=self.OFDR_plot.plot(pen='y')
        self.plot_processed_data()
    
    def ClearButtonClicked(self):
        self.OFDR_plot.clear()
        self.plot_initialize()

    def receive_tel(self,s):
        if s=='disconnect':
            self.tel.ser.close()
            del self.tel
            self.statusBar().showMessage('TLS8164A: Disconnected.')
        else:
            self.tel=s
            self.statusBar().showMessage('TLS8164A: Connection established.')

    def receive_data(self,s):
        self.channel_data=s[0]
        self.t_data=np.arange(0,s[1]['Common']['Length']/s[1]['Common']['SampleRate'],1/s[1]['Common']['SampleRate'])
        self.RunMessageplainTextEdit.appendPlainText('Receive ADC data')
        
    def AutoMeasureButtonClicked(self):
        self.measuring=True
        self.AutoMeasurepushButton.setEnabled(False)
        self.AutoMeasurepushButton.setText('Measuring')
        with open('OFDR_Gage.json','r') as f:
            settings_dict_Gage=json.load(f)
        with open('OFDR_TLS_8164A.json','r') as f:
            settings_dict_TLS_8164A=json.load(f)
            
        def Run_worker_Run_TLS_8164A():
            worker_Run_TLS_8164A=Work_Run_TLS_8164A(self.tel,settings_dict_TLS_8164A)
            worker_Run_TLS_8164A.signals.finished.connect(Run_worker_single_Gage)
            self.threadpool.start(worker_Run_TLS_8164A)
            self.RunMessageplainTextEdit.appendPlainText('TLS sweep start')

        def Run_worker_single_Gage():
            worker_single_Gage=Work_single_Gage(self.inst_Gage,settings_dict_Gage,'ascii')
            worker_single_Gage.signals.result.connect(self.receive_data)
            worker_single_Gage.signals.finished.connect(Run_worker_OFDR_Analysis)
            self.threadpool.start(worker_single_Gage)
            self.RunMessageplainTextEdit.appendPlainText('ADC_single start')

        def Run_worker_OFDR_Analysis():
            AUX_delay_length=20
            self.data=np.vstack((self.t_data,self.channel_data))
            worker_OFDR_Analysis=Work_Analysis(self.data,AUX_delay_length)
            worker_OFDR_Analysis.signals.result.connect(self.receive_processed_data)
            worker_OFDR_Analysis.signals.finished.connect(Run_worker_Stop_TLS_8164A)
            self.threadpool.start(worker_OFDR_Analysis)
            self.RunMessageplainTextEdit.appendPlainText('Analyzing data...')
            self.statusBar().showMessage('Analyzing data...')
            
        def Run_worker_Stop_TLS_8164A():
            worker_Stop_TLS_8164A=Work_Stop_TLS_8164A(self.tel)
            self.threadpool.start(worker_Stop_TLS_8164A)
            self.RunMessageplainTextEdit.appendPlainText('TLS stop')
            self.AutoMeasurepushButton.setEnabled(True)
            self.AutoMeasurepushButton.setText('Auto Measure')
            self.measuring=False
            
        Run_worker_Run_TLS_8164A()

    def FindpeakButtonClicked(self):
        print('Not working')
        
    def plot_processed_data(self):
        try:
            s=self.processed_data
        except:
            self.statusBar().showMessage('No data')
        else:
            self.statusBar().showMessage('Plotting data...')
            if self.LogscalecheckBox.isChecked():
                try:
                    self.plt.setData(1000*np.pi*self.processed_data[0],20*np.log10(self.processed_data[1]))
                except:
                    self.statusBar().showMessage('Error occurred during plotting data')
                else:
                    self.OFDR_plot.plotItem.setLabels(left='Reflectance (dB)',bottom='Distance (mm)')
                    self.OFDR_plot.setYRange(-140,-20)
                    self.statusBar().showMessage('Processing complete')
                    self.RunMessageplainTextEdit.appendPlainText('Plot update complete')
            else:
                try:
                    self.plt.setData(1000*np.pi*self.processed_data[0],self.processed_data[1]) # 아래 해설 참고
                except:
                    self.statusBar().showMessage('Error occurred during plotting data')
                else:
                    self.OFDR_plot.plotItem.setLabels(left='Reflection coefficient',bottom='Distance (mm)')
                    self.OFDR_plot.setYRange(0,0.1)
                    self.statusBar().showMessage('Processing complete')
                    self.RunMessageplainTextEdit.appendPlainText('Plot update complete')
            
    def receive_processed_data(self,s):
        self.processed_data=s
        self.plot_processed_data()

class WorkerSignals(QObject):
    finished=pyqtSignal()
    error=pyqtSignal(tuple)
    result=pyqtSignal(object)
    progress=pyqtSignal(int)

class Work_Analysis(QRunnable):
    def __init__(self,data,AUX_delay_length):
        super().__init__()
        self.signals=WorkerSignals()
        self.data=data
        self.AUX_delay_length=AUX_delay_length
        
    def run(self):
        self.data[2]=signal_filter1(self.data[2])
        x,y=zero_crossing_resampler3(self.data[0],self.data[1],self.data[2],'even')
        y=rejection_filter_of_linear_component(x,y)
        f,y_fft=sp_fft_abs(y*sp.signal.windows.flattop(y.size),2*np.pi/self.AUX_delay_length)
        cal_factor=(max(self.data[2])-min(self.data[2]))*10**-0.6576763016665754
        y_fft=y_fft*cal_factor
        self.signals.result.emit(np.vstack((f,y_fft)))
        self.signals.finished.emit()


if __name__ == "__main__":
    app=QApplication(sys.argv)
    mainWindow=Analysis_OFDR_Window()
    app.exec()


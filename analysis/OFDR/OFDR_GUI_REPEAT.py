from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

import csv
import datetime
import pyqtgraph as pg
import time,sys,traceback,os,json,configparser
import numpy as np
import scipy as sp
import pandas as pd
import threading
from scipy.signal import find_peaks
from analysis_tools import *
from dev import *
from TimedCalls import TimedCalls
sys.path.append('../..')



form_class_Analysis_OFDR = uic.loadUiType('C:\\GUI\\analysis\\OFDR\\OFDR.ui')[0]
class Analysis_OFDR_Window(QMainWindow,form_class_Analysis_OFDR,object):
    work_requested = pyqtSignal(int,int)
    def __init__(self,*args,**kwargs):
        self.threadpool=QThreadPool()
        super(QMainWindow, self).__init__()


        self.setupUi(self)
        self.show()
        self.threadpool=QThreadPool()
        self.plot_initialize()
        self.init_connection()
        self.measuring=False

        self.test_id = sys.argv[1]
        self.iteration_time = int(sys.argv[2])
        self.total_time = int(sys.argv[3])
        self.peak_start = int(sys.argv[4])
        self.peak_end = int(sys.argv[5])
        self.file_path = sys.argv[6]

        self.worker = Worker()
        self.worker_thread = QThread()
        self.worker.progress.connect(self.update_progress)


        self.work_requested.connect(self.worker.do_work)

        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.start()

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
        self.start(self.iteration_time,self.total_time)
    def RepeatMeasureButtonClicked(self):
        print('clicked')

        self.measuring=True
        self.start_time=datetime.datetime.now()
        self.AutoMeasurepushButton.setEnabled(False)
        self.AutoMeasurepushButton.setText('Measuring')
        with open('OFDR_Gage.json','r') as f:
            settings_dict_Gage=json.load(f)
        with open('OFDR_TLS_8164A.json','r') as f:
            settings_dict_TLS_8164A=json.load(f)



        def Run_worker_Run_TLS_8164A():
            self.measured_time = datetime.datetime.now()
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








        # # Start test a few secs from now.
        # start_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
        # run_time = datetime.timedelta(minutes=self.total_time)  # How long to iterate function.
        # end_time = start_time + run_time
        #
        # assert start_time > datetime.datetime.now(), 'Start time must be in future'
        #
        # timed_calls = TimedCalls(Run_worker_Run_TLS_8164A, self.iteration_time)  # Thread to call function every [iteration_time] secs.
        #
        # print(f'waiting until {start_time.strftime("%H:%M:%S")} to begin...')
        # wait_time = start_time - datetime.datetime.now()
        # time.sleep(wait_time.total_seconds())
        #
        # print('starting ... until end time: ', end_time.strftime("%H:%M:%S"))
        # timed_calls.start()  # Start thread.
        # while datetime.datetime.now() < end_time:
        #     time.sleep(1)  # Twiddle thumbs while waiting.
        # print('done at ', datetime.datetime.now().strftime("%H:%M:%S"))
        # timed_calls.cancel()



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
                    x=1000*np.pi*self.processed_data[0]
                    y=20*np.log10(self.processed_data[1])
                    self.plt.setData(x,y)
                except:
                    self.statusBar().showMessage('Error occurred during plotting data')
                else:
                    self.OFDR_plot.plotItem.setLabels(left='Reflectance (dB)',bottom='Distance (mm)')
                    self.OFDR_plot.setYRange(-140,-20)
                    self.statusBar().showMessage('Processing complete')
                    self.RunMessageplainTextEdit.appendPlainText('Plot update complete')
                    self.save_data(x, y)
            else:
                try:
                    x=1000*np.pi*self.processed_data[0]
                    y=self.processed_data[1]
                    self.plt.setData(x, y) # 아래 해설 참고
                except:
                    self.statusBar().showMessage('Error occurred during plotting data')
                else:
                    self.OFDR_plot.plotItem.setLabels(left='Reflection coefficient',bottom='Distance (mm)')
                    self.OFDR_plot.setYRange(0,0.1)
                    self.statusBar().showMessage('Processing complete')
                    self.RunMessageplainTextEdit.appendPlainText('Plot update complete')
                    self.save_data(x, y)
    def start(self,iteration_time,total_time):

        self.work_requested.emit(iteration_time,total_time)
        print(iteration_time,total_time)

    def update_progress(self,i):
        self.RepeatMeasureButtonClicked()


    def receive_processed_data(self,s):
        self.processed_data=s
        self.plot_processed_data()

    def save_data(self,x,y):
        arr = np.array([x,y])
        arr = np.transpose(arr)
        np.savetxt(self.file_path+'/'+self.test_id+'_'+self.measured_time.strftime('%Y%m%d%H%M')+'.csv', arr, delimiter=',', header='Distance,Reflection_Coefficient')
        print(self.file_path+'/'+self.test_id+'_'+self.measured_time.strftime('%Y%m%d%H%M')+'.csv '+'saved.\n')

class WorkerSignals(QObject):
    finished=pyqtSignal()
    error=pyqtSignal(tuple)
    result=pyqtSignal(object)
    progress=pyqtSignal(int)

class Worker(QObject):
    progress= pyqtSignal(int,int)


    @pyqtSlot(int,int)
    def do_work(self,iteration_time,total_time):
        for i in range(int(total_time*60/iteration_time)):
            print('click # ', i+1)
            self.progress.emit(i,i)
            time.sleep(iteration_time)



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


def main():
    test_id = sys.argv[1]
    iteration_time = int(sys.argv[2])
    total_time = int(sys.argv[3])
    peak_start = int(sys.argv[4])
    peak_end = int(sys.argv[5])
    file_path = sys.argv[6]

    result = 0

    def ui_thread(app):
        """a thread for QApplication event loop"""
        app[0]=QApplication(sys.argv)
        app[0].exec_()
    try:
        app=QApplication(sys.argv)
        w=Analysis_OFDR_Window()
        app.exec()










    except Exception as e:
        print(e)
        result = 1
    finally :
        sys.exit(result)

if __name__=='__main__':
    main()


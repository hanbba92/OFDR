from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import uic
import pyvisa
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
sys.path.append('../..')
from dev import *



#TabWidget
import plotly.offline as po
import plotly.graph_objs as go
import plotly.express as px



form_class_Analysis_OFDR = uic.loadUiType('C:\\GUI\\analysis\\OFDR\\OFDR.ui')[0]
class Analysis_OFDR_Window(QMainWindow,form_class_Analysis_OFDR,object):


    def __init__(self,*args,**kwargs):
        self.threadpool=QThreadPool()
        super(QMainWindow, self).__init__()
        self.count=0


        self.setupUi(self)
        self.show()
        self.threadpool=QThreadPool()
        self.plot_initialize()
        self.init_connection()
        self.measuring=False
        self.iteration_start=False
        self.data_path = 'C:/OFDR_DATA'
        if len(sys.argv) > 2:
            print(sys.argv[1])
            self.data_path = sys.argv[1]
        self.IterationTimeText.setReadOnly(False)
        self.IterationTimeText.setReadOnly(False)





        #tab widget
        self.AddPlotButton.clicked.connect(self.getFile)
        self.plot_initialize_tab2()
        self.PlottingTab.setCurrentIndex(0)



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


    #Tab Widget
    def plot_initialize_tab2(self):
        self.fig = go.Figure([])
        self.fig.update_layout(
            yaxis_title='Reflection_Coefficient (dB)',
            xaxis_title='Distance (mm)',
            title=dict(text= 'OFDR', x = 0.5, xanchor = 'center'),
            hovermode='x',
            legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01),
            showlegend=True
        )

        self.show_qt(self.fig)
    def getFile(self):
        """This function wil get the address of the file location"""
        self.filenames =QFileDialog.getOpenFileNames(directory=self.data_path)[0]
        self.RunMessageplainTextEdit.appendPlainText('Updating Plot...')
        self.filedims = len(self.filenames)
        self.fig_list=[]
        self.color_list=[
                        '#1f77b4',  # muted blue
                        '#ff7f0e',  # safety orange
                        '#2ca02c',  # cooked asparagus green
                        '#d62728',  # brick red
                        '#9467bd',  # muted purple
                        '#8c564b',  # chestnut brown
                        '#e377c2',  # raspberry yogurt pink
                        '#7f7f7f',  # middle gray
                        '#bcbd22',  # curry yellow-green
                        '#17becf'   # blue-teal
                    ]
        if self.filedims != 0:
            for i in range(self.filedims):
                if self.filenames[i][-3:] =='npy':
                    self.f=np.load(self.filenames[i])
                elif self.filenames[i][-3:] =='csv':
                    self.f=np.loadtxt(self.filenames[i], delimiter=',', dtype='float64')
                    self.f=self.f.transpose()
                else:
                    self.RunMessageplainTextEdit.appendPlainText('Invalid File Format. Accepted Formats: npy or csv')
                    continue
                self.fig_list.append( go.Scatter(name=self.filenames[i][-18:-4],
                                x=self.f[0],
                                y=self.f[1],
                                mode='lines',
                                line=dict(color=self.color_list[i])
                                ))

            self.fig = go.Figure(self.fig_list)
            self.fig.update_layout(
                yaxis_title='Reflection_Coefficient (dB)',
                xaxis_title='Distance (mm)',
                title=dict(text=self.filenames[0][-27:-19], x = 0.5, xanchor = 'center'),
                hovermode='x',
                legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01),
                showlegend=True
            )

            self.show_qt(self.fig)


    def show_qt(self,fig):
        raw_html = '<html><head><meta charset="utf-8" />'
        raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_html += '<body>'
        raw_html += po.plot(fig, include_plotlyjs=False, output_type='div')
        raw_html += '</body></html>'



        self.fig_view = self.MultiplePlotView
        # setHtml has a 2MB size limit, need to switch to setUrl on tmp file
        # for large figures.
        plot_path= self.data_path + '/' + 'file.html'
        fig.write_html(plot_path)
        self.fig_view.load(QUrl.fromLocalFile(plot_path))
        self.fig_view.show()
        if fig['data']:
            self.RunMessageplainTextEdit.appendPlainText('Plot Update Completed!')


    def RepeatMeasureButtonClicked(self):
        self.model_number = self.ModelSerialNumber.text()
        if len(self.model_number) == 0:
            self.RunMessageplainTextEdit.appendPlainText('Please Insert Model S/N')
        else:
            self.ModelSerialNumber.setReadOnly(True)
            self.save_file_path = self.data_path + '/' + self.model_number
            try:
                global iteration_time, total_time
                iteration_time = int(self.IterationTimeText.text())
                self.IterationTimeText.setReadOnly(True)
                total_time = int(self.TotalTimeText.text())
                self.TotalTimeText.setReadOnly(True)
                self.RepeatMeasurepushButton.setEnabled(False)
                self.AutoMeasurepushButton.setEnabled(False)
            except Exception as e:
                self.RunMessageplainTextEdit.appendPlainText('Please Insert Integer Values in Iteration Time(s) and Total Time(min)')
            else:
                self.iteration_start=True
                self.total_iteration=self.count
                self.measuring = True
                self.start_time = datetime.datetime.now()
                self.RepeatMeasurepushButton.setText('Measuring')
                self.worker = WorkerSignals()
                self.thread = QThread()
                self.worker.moveToThread(self.thread)
                self.IterationTimeText.setReadOnly(True)
                self.TotalTimeText.setReadOnly(True)
                self.RunMessageplainTextEdit.appendPlainText('Iteration Time: {} sec, Total Time: {} min'.format(iteration_time,total_time))
                self.total_iteration+=int(total_time*60/iteration_time)
                self.thread.started.connect(self.worker.SetMeasurement)
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.Reset_Measure_Btn)
                self.worker.progress.connect(self.Run_worker_Run_TLS_8164A)
                self.thread.start()








    def AutoMeasureButtonClicked(self):
        self.model_number = self.ModelSerialNumber.text()
        if len(self.model_number) == 0:
            self.RunMessageplainTextEdit.appendPlainText('Please Insert Model S/N')
        else:
            self.ModelSerialNumber.setReadOnly(True)
            self.save_file_path = self.data_path + '/' + self.model_number
            self.AutoMeasurepushButton.setEnabled(False)
            self.RepeatMeasurepushButton.setEnabled(False)
            self.total_iteration = self.count+1
            self.measuring = True
            self.start_time = datetime.datetime.now()

            self.AutoMeasurepushButton.setText('Measuring')
            self.worker=WorkerSignals()
            self.thread = QThread()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.SingleMeasure)
            self.worker.finished.connect(self.thread.quit)
            self.worker.progress.connect(self.Run_worker_Run_TLS_8164A)
            self.thread.start()




    def StopButtonClicked(self):
        if self.measuring:
            self.RunMessageplainTextEdit.appendPlainText('Cannot stop while measuring')
        else:
            if self.iteration_start:
                self.iteration_start = False
                self.threadpool.start(self.worker.BreakLoop)
                self.threadpool.start(self.Reset_Measure_Btn)
                self.RunMessageplainTextEdit.appendPlainText('Iteration Stopped')


    def Run_worker_Run_TLS_8164A(self):

        with open('OFDR_TLS_8164A.json', 'r') as f:
            settings_dict_TLS_8164A = json.load(f)
        self.measured_time = datetime.datetime.now()
        self.TemperatureText.setReadOnly(True)
        worker_Run_TLS_8164A=Work_Run_TLS_8164A(self.tel,settings_dict_TLS_8164A)
        worker_Run_TLS_8164A.signals.finished.connect(self.Run_worker_single_Gage)
        self.threadpool.start(worker_Run_TLS_8164A)
        self.count += 1
        self.RunMessageplainTextEdit.appendPlainText('# {}'.format(self.count))
        self.RunMessageplainTextEdit.appendPlainText('TLS sweep start')

    def Run_worker_single_Gage(self):
        with open('OFDR_Gage.json', 'r') as f:
            settings_dict_Gage = json.load(f)
        worker_single_Gage=Work_single_Gage(self.inst_Gage,settings_dict_Gage,'ascii')
        worker_single_Gage.signals.result.connect(self.receive_data)
        worker_single_Gage.signals.finished.connect(self.Run_worker_OFDR_Analysis)
        self.threadpool.start(worker_single_Gage)
        self.RunMessageplainTextEdit.appendPlainText('ADC_single start')

    def Run_worker_OFDR_Analysis(self):
        AUX_delay_length=20
        self.data=np.vstack((self.t_data,self.channel_data))
        worker_OFDR_Analysis=Work_Analysis(self.data,AUX_delay_length)
        worker_OFDR_Analysis.signals.result.connect(self.receive_processed_data)
        worker_OFDR_Analysis.signals.finished.connect(self.Run_worker_Stop_TLS_8164A)
        self.threadpool.start(worker_OFDR_Analysis)
        self.RunMessageplainTextEdit.appendPlainText('Analyzing data...')
        self.statusBar().showMessage('Analyzing data...')

    def Run_worker_Stop_TLS_8164A(self):

        worker_Stop_TLS_8164A=Work_Stop_TLS_8164A(self.tel)
        self.threadpool.start(worker_Stop_TLS_8164A)
        self.RunMessageplainTextEdit.appendPlainText('TLS stop')
        x = 1000 * np.pi * self.processed_data[0]
        y = 20 * np.log10(self.processed_data[1])
        self.save_data(x, y)
        self.measuring = False
        if self.total_iteration == self.count:
            self.iteration_start = False
            self.threadpool.start(self.worker.BreakLoop)
            self.threadpool.start(self.Reset_Measure_Btn)





    def Reset_Measure_Btn(self):
        self.AutoMeasurepushButton.setEnabled(True)
        self.RepeatMeasurepushButton.setEnabled(True)
        self.AutoMeasurepushButton.setText('Single Measure')
        self.RepeatMeasurepushButton.setText('Repeat Measure')
        self.measuring = False
        self.IterationTimeText.setReadOnly(False)
        self.TotalTimeText.setReadOnly(False)
        self.ModelSerialNumber.setReadOnly(False)
        self.TemperatureText.setReadOnly(False)












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




    def receive_processed_data(self,s):
        self.processed_data=s
        self.plot_processed_data()

    def save_data(self,x,y):

        arr = np.array([x,y])
        if not os.path.exists(self.save_file_path):
            os.makedirs(self.save_file_path)
        self.my_instrument = 0
        if self.ChamberCheckBox.isChecked():

            rm = pyvisa.ResourceManager()

            for i in rm.list_resources():
                if i[0] == 'G':
                    print(i)
                    self.my_instrument = rm.open_resource(i)
                    break
        if self.my_instrument:
            self.message = self.my_instrument.query('TEMP?')
            self.cur_temp=self.message.split(',')[0]
        else:
            self.cur_temp= self.TemperatureText.text()

        self.file_path=self.save_file_path+'/'+self.measured_time.strftime('%Y_%m_%d_%H.%M.%S_')+self.cur_temp
        self.RunMessageplainTextEdit.appendPlainText(self.file_path+'.npy'+' saved.')
        np.save(self.file_path+'.npy', arr)

    def mon(self,cmd):
        self.message=self.instrument.query(cmd)

    def get_temp(self,my_instrument):
        self.instrument=my_instrument
        return self.mon('TEMP?')

    def no_chamber(self,my_instrument):
        self.message='None'



class WorkerSignals(QObject):
    single=pyqtSignal()
    finished=pyqtSignal()
    error=pyqtSignal(tuple)
    result=pyqtSignal(object)
    progress=pyqtSignal()
    iterationstop=pyqtSignal()

    def __init__(self):
        super().__init__()
        self.loop=False


    @pyqtSlot()
    def SetMeasurement(self):
        self.loop=True


        for i in range(int(total_time*60/iteration_time)):
            if not self.loop:
                break
            self.progress.emit()
            for _ in range(iteration_time*2):
                if not self.loop:
                    break
                time.sleep(0.5)
        self.finished.emit()


    def BreakLoop(self):
        self.loop =False

    def SingleMeasure(self):

        self.progress.emit()
        self.finished.emit()






    def SetTime(self,iteration_time,total_time):
        self.settime.emit(iteration_time,total_time)




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

    result = 0

    def ui_thread(app):
        """a thread for QApplication event loop"""
        app[0]=QApplication(sys.argv)
        app[0].exec_()
    try:
        sys.argv.append("--disable-web-security")
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


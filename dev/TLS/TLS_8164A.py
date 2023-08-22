from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import serial
import serial.tools.list_ports as stlp
import time,sys,traceback,os,datetime

class tel_serial:
    def __init__(self):
        pass

    def serial_list(self):
        list_comports=stlp.comports()
        return ['%s: %s' %(val.device,val.description) for val in list_comports]
    
class tls8164A_serial:
    def __init__(self,port,baud):
        self.ser=serial.Serial(port,baud,timeout=1)

    def handshake_check(self):
        handshake_count=0
        while handshake_count<3:
            self.ser.write(b'*IDN?\n')
            time.sleep(0.2)
            Rxmessage=self.ser.readline().decode('utf-8')
            if Rxmessage!='':
                return Rxmessage
            handshake_count+=1
        return 'Timeout reached'            

    def send(self,cmd):
        self.ser.write(bytes(cmd+'\n','utf-8'))
        while True:
            if cmd[-1]!='?':
                self.ser.write(b'*OPC?\n')
            time.sleep(0.2)
            Rxmessage=self.ser.readline().decode('utf-8')
            if Rxmessage!='':
                return Rxmessage
                break

    def initialize(self):
        self.send(':WAVelength:SWEep STOP')
        self.send(':OUTPut0 0')
        self.send('*RST')

    def run_sweep(self,settings_dict):
        self.send(':OUTPut0:PATH '+settings_dict['path'])
        self.send(':OUTPut0 1')
        self.send(':AM:STATe 0')
        self.send(':WAVelength:SWEep:CYCLes 0')
        self.send(':WAVelength:SWEep:MODE CONTinuous')
        self.send(':WAVelength:SWEep:SPEed '+settings_dict['speed'])
        self.send(':WAVelength:SWEep:STARt '+settings_dict['start_wl']+'nm')
        self.send(':WAVelength:SWEep:STOP '+settings_dict['stop_wl']+'nm')
        self.send(':POWer '+settings_dict['power']+'mw')
        self.send(':TRIGger:OUTPut SWSTarted')
        self.send(':WAVelength:SWEep START')

    def stop(self):
        self.send(':WAVelength:SWEep STOP')
        self.send(':OUTPut0 0')
        

form_class_Connection_TLS_8164A = uic.loadUiType('C:\\GUI\\dev\\TLS\\Connection_TLS_8164A.ui')[0]
class Connection_TLS_8164A_Window(QMainWindow,form_class_Connection_TLS_8164A):
    def __init__(self,*args,**kwargs):
        super().__init__()
        self.setupUi(self)
        self.threadpool=QThreadPool()
        self.RefreshButtonClicked()
        self.to_main_signals=WorkerSignals()
        self.kwargs=kwargs
        if 'tel' in self.kwargs:
            self.ConnectButton.setText('Disconnect')
            self.tel=self.kwargs['tel']
        else:
            self.ConnectButton.setText('Connect')

    def RefreshButtonClicked(self):
        serial_list=tel_serial()
        self.PORTcomboBox.clear()
        self.PORTcomboBox.addItems(serial_list.serial_list())

    def ConnectButtonClicked(self):
        if 'tel' in self.kwargs:
            del self.tel
            self.statusBar().showMessage('Disconnected')
            self.ConnectButton.setText('Connect')
            self.to_main_signals.result.emit('disconnect')
            self.close()
        else:
            work=Work_Connect_TLS_8164A(self.PORTcomboBox.currentText().split(':')[0],self.BAUDcomboBox.currentText())
            work.signals.result.connect(self.receive_tel)
            work.signals.progress.connect(self.connection_progress)
            self.threadpool.start(work)
            self.ConnectButton.setText('Connecting...')
            self.statusBar().showMessage('Connecting %s...'%self.PORTcomboBox.currentText())

    def receive_tel(self,s):
        if s[0]!='':
            self.statusBar().showMessage('Connection established. %s @ %s'%(self.PORTcomboBox.currentText(),s[-1]))
            self.ConnectButton.setText('Disconnect')
            self.to_main_signals.result.emit(s[0])
            self.close()
            return s[0]
        else:
            self.statusBar().showMessage('Connection failed')
            self.ConnectButton.setText('Connect')
            return 'Connection failed'

    def connection_progress(self,i):
        self.statusBar().showMessage('Connecting %s @ %i...'%(self.PORTcomboBox.currentText(),i))

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class Work_Connect_TLS_8164A(QRunnable):
    def __init__(self,port,baud):
        super().__init__()
        self.signals=WorkerSignals()
        self.port=port
        self.baud=baud
        
    def run(self):
        if self.baud=='Auto':
            baud_list=[38400,19200,9600]
            for i,b in enumerate(baud_list):
                self.signals.progress.emit(int(b))
                self.tel=tls8164A_serial(self.port,b)
                handshake_result=self.tel.handshake_check()
                if handshake_result != 'Timeout reached':
                    self.signals.result.emit((self.tel,handshake_result,b))
                    break
                elif i<len(baud_list)-1:
                    del self.tel
                else:
                    del self.tel
                    self.signals.result.emit(('',handshake_result,''))
        else:
            self.tel=tls8164A_serial(self.port,self.baud)
            handshake_result=self.tel.handshake_check()
            if handshake_result == 'Timeout reached':
                self.signals.result.emit(('',handshake_result,self.baud))
            else:
                self.signals.result.emit((self.tel,handshake_result,self.baud))

class Work_Run_TLS_8164A(QRunnable):
    def __init__(self,tel,settings_dict):
        super().__init__()
        self.signals=WorkerSignals()
        self.tel=tel
        self.settings_dict=settings_dict
        
    def run(self):
        self.tel.run_sweep(self.settings_dict)
        self.signals.finished.emit()

class Work_Stop_TLS_8164A(QRunnable):
    def __init__(self,tel):
        super().__init__()
        self.signals=WorkerSignals()
        self.tel=tel
        
    def run(self):
        self.tel.stop()

class Work_Initialize_TLS_8164A(QRunnable):
    def __init__(self,tel):
        super().__init__()
        self.signals=WorkerSignals()
        self.tel=tel

    def run(self):
        self.tel.initialize()




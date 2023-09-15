from PyQt5.QtCore import *
import pyvisa

class ESPEC_Monitor(QRunnable):
    def __init__(self,my_instrument):
        self.instrument = my_instrument

    def run(self):
        rm = pyvisa.ResourceManager()
        self.my_instrument = 0
        for i in rm.list_resources():
            if i[0] == 'G':
                self.my_instrument = rm.open_resource(i)
                break
        if self.my_instrument:

            self.to_main_signals.result.emit(self.my_instrument)
        else:
            self.to_main_signals.progress.emit(0)


    def mon(self,cmd):
        self.message= self.instrument.query(cmd)
        return self.message.split()


    def get_temp(self):
        self.mon('TEMP?')

class ESPEC(QRunnable):
    def __init__(self):
        super().__init__()
        self.threadpool=QThreadPool()
        self.to_main_signals=WorkerSignals()

    def run(self):
        rm = pyvisa.ResourceManager()
        self.my_instrument = 0
        for i in rm.list_resources():
            if i[0] == 'G':
                self.my_instrument = rm.open_resource(i)
                break
        if self.my_instrument:
            self.to_main_signals.result.emit(self.my_instrument)
        else:
            self.to_main_signals.progress.emit(1)


    def receive_tel(self,my_instrument):
        self.Monitor = ESPEC_Monitor(my_instrument)
        return self.Monitor

    def connection_progress(self):
        return 0

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(int)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


from PyQt5 import QtWidgets, uic, QtCore, QtGui
import sys
from pyqtgraph import PlotWidget
import pyqtgraph
import numpy as np
import time
import serial
import os

ser = serial.Serial('/dev/tty.usbmodem14201', 9600,timeout=3)
ser.reset_input_buffer()

class Ui(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):    
        super(Ui, self).__init__(*args, **kwargs)
        uic.loadUi('../ui_files/mainwindow.ui', self)

        self.btn_save.clicked.connect(self.btn_save_func)
        self.btn_cancel.clicked.connect(app.instance().quit)
        
        # Plot Style
        self.graph_cycle.setLabel('left', 'Temperature', units='C')
        self.graph_cycle.setLabel('bottom', 'Cycle Number')
        self.graph_cycle.setTitle('Cycling Graph')
        self.graph_cycle.setBackground('w')
        self.graph_cycle.showGrid(x=True, y=True)

        # Plot Reference
        # self.temp = list(range(300))
        self.temp = [0]*300
        self.time = [0]*300
        self.dt = 1000 # ms
        pen = pyqtgraph.mkPen(color=(255, 0, 0))
        self.plot_ref = self.graph_cycle.plot(self.temp, self.time, pen=pen)

        self.tab_main.setCurrentIndex(0)
        
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.dt)
        self.timer.timeout.connect(self.update_plot_data)

        self.timer.start()
        self.show()

    def btn_save_func(self):
        self.lbl_test.setText(self.le_name.text())

    def read_data(self):
        # print("Reading data")
        # if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        # print(line)
        args = line.split("\t")
        mode = args[0]
        cycle_stage = args[1]
        current_temp = args[2]
        state = args[3]
        if state=="#":
            print("TRIGGER!")
            f = os.system("ls")
            print(f)
        # print(f"current_temp: {current_temp}")
        current_power = args[3]
        self.lbl_test.setText(current_temp)
        # print(f"current temp ")
        # print(current_temp)
        return float(current_temp)
    
    def update_plot_data(self):
        self.time = self.time[1:]  # Remove the first y element.
        self.time.append(self.time[-1] +1)  # Add a new value 1 higher than the last.
        # print(self.time)
        self.temp = self.temp[1:]  # Remove the first
        try:
            self.temp.append(self.read_data()) # Add a new random value.
        except:
            pass
        # print(self.temp)
        self.plot_ref.setData(self.time, self.temp)  # Update the data.
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()

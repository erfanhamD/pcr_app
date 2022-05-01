from PyQt5 import QtWidgets, uic, QtCore, QtGui
import sys
from pyqtgraph import PlotWidget
import numpy as np
import time
import serial

ser = serial.Serial('/dev/tty.usbmodem14301', 9600,timeout=3)
ser.reset_input_buffer()

class Ui(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):    
        super(Ui, self).__init__(*args, **kwargs)
        uic.loadUi('../ui_files/mainwindow.ui', self)
        self.btn_save.clicked.connect(self.btn_save_func)
        self.btn_cancel.clicked.connect(app.instance().quit)
        self.btn_plot.clicked.connect(self.plot)
        # self.plot([1,2,3,4,5,6,7,8,9,10], [30,32,34,32,33,31,29,32,35,45])
        self.tab_main.setCurrentIndex(0)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.read_data)
        data = self.read_data()
        print(f"data is = {data}")
        self.lbl_test.setText(data)
        self.timer.start()
        self.show()

    def btn_save_func(self):
        self.lbl_test.setText(self.le_name.text())

    def plot(self, hour, temperature):
        self.plot_ref = self.graph_cycle.plot(hour, temperature)
        self.graph_cycle.setLabel('left', 'Temperature', units='C')
        self.graph_cycle.setLabel('bottom', 'Cycle Number')
        self.graph_cycle.setTitle('Cycling Graph')
        self.graph_cycle.showGrid(x=True, y=True)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)
        # self.timer.timeout.connect(self.update_plot)
        data = self.read_data()
        # print(f"data is = {data}")
        self.lbl_test.setText(data)
        self.timer.start()

    def read_data(self):
        if ser.in_waiting > 0:
            # time.sleep(1)
            line = ser.readline().decode('utf-8').rstrip()
            args = line.split(",")
            mode = args[0]
            cycle_stage = args[1]
            current_temp = args[2]
            current_power = args[3]
            peltier_status = args[4]
            cycle_No = args[5]
            # print(f"current temp is = {current_temp}")
            # print(type(current_temp))
            self.lbl_test.setText(current_temp)
            return current_temp
        
    
    def update_plot(self):
        self.x = []
        self.y.append(self.read_data())
        self.plot_ref.setData(self.x, self.y)
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()

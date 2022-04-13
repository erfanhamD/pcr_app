from PyQt5 import QtWidgets, uic, QtCore
import sys
from pyqtgraph import PlotWidget
import numpy as np

class Ui(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):    
        super(Ui, self).__init__(*args, **kwargs)
        uic.loadUi('../ui_files/mainwindow.ui', self)
        self.btn_save.clicked.connect(self.btn_save_func)
        self.btn_cancel.clicked.connect(app.instance().quit)
        self.plot([1,2,3,4,5,6,7,8,9,10], [30,32,34,32,33,31,29,32,35,45])
        self.tab_main.setCurrentIndex(0)
        self.show()

    def btn_save_func(self):
        self.lbl_test.setText(self.le_name.text())

    def plot(self, hour, temperature):
        self.graph_cycle.plot(hour, temperature)
        self.graph_cycle.setLabel('left', 'Temperature', units='C')
        self.graph_cycle.setLabel('bottom', 'Cycle Number')
        self.graph_cycle.setTitle('Cycling Graph')
        self.graph_cycle.showGrid(x=True, y=True)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()

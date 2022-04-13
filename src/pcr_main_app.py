from PyQt5 import QtWidgets, uic, QtCore
import sys
from pyqtgraph import PlotWidget

# import matplotlib
# matplotlib.use('Qt5Agg')

# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# from matplotlib.pyplot import Figure
import numpy as np

class Ui(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):    
        super(Ui, self).__init__(*args, **kwargs)
        uic.loadUi('../ui_files/mainwindow.ui', self)
        
        self.btn_save.clicked.connect(self.btn_save_func)
        self.btn_cancel.clicked.connect(app.instance().quit)
        # self.lbl_plot.setText("Hi")
        # tab_main = self.tab_main()
        # tab_main.setTabText(0, "Main")
        self.show()
    def btn_save_func(self):
        self.lbl_test.setText(self.le_name.text())

# class tab_main(QtWidgets.QTabWidget):
#     def __init__(self):
#         super(tab_main, self).__init__()
#         uic.loadUi('ui_files/tab_main.ui', self)
#         self.btn_save.clicked.connect(self.btn_save_func)
#         self.btn_cancel.clicked.connect(app.instance().quit)
#         self.show()

#     def btn_save_func(self):
#         self.lbl_test.setText(self.le_name.text())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()

from PyQt5 import QtWidgets, uic
import sys

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('ui_files/mainwindow.ui', self)
        self.btn_save.clicked.connect(self.btn_save_func)
        self.btn_cancel.clicked.connect(app.instance().quit)
        self.show()
    def btn_save_func(self):
        self.lbl_test.setText(self.le_name.text())



        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
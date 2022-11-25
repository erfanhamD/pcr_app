from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import QObject, QThread
import sys
from contextlib import contextmanager
from datetime import datetime
from pyqtgraph import PlotWidget
import pyqtgraph
import numpy as np
import time
import serial
import os
import csv
import pandas as pd
import threading
import cv2
import logging
import glob
from pathlib import Path

def circle_intensity(x_c, y_c, R, img):
    sum_int = [0, 0, 0]
    for x_r in range(x_c-R, x_c+R):
        for y_r in range(y_c-R, y_c+R):
            if(((x_r-x_c)**2 + (y_r-y_c)**2) < R**2):
                sum_int[0] = sum_int[0] + img[y_r, x_r][0]
                sum_int[1] = sum_int[1] + img[y_r, x_r][1]
                sum_int[2] = sum_int[2] + img[y_r, x_r][2]
    return sum_int[1]/1_000_000

def marker_locater(image_address):
    marker_img = cv2.imread(image_address, 0)
    marker_img = cv2.medianBlur(marker_img,91)
    img_h, img_w = marker_img.shape
    marker_img = marker_img[int(img_h/2)-int(img_h/8):int(img_h/2)+int(img_h/8), int(img_w/2)-int(img_w/8):int(img_w/2)+int(img_w/8)]
    marker_circles = cv2.HoughCircles(marker_img,cv2.HOUGH_GRADIENT,1,250,
                                param1=30,param2=15,minRadius=0,maxRadius=80)
    # convert the circles into integers
    marker_circles = np.uint16(np.around(marker_circles))
    # translate the marker circles to the original image
    marker_circles[0,:,0] = marker_circles[0,:,0] + int(img_w/2)-int(img_w/8)
    marker_circles[0,:,1] = marker_circles[0,:,1] + int(img_h/2)-int(img_h/8)
    # calculate the center of the line between the two marker_circles' centers
    line_center_x = (marker_circles[0,0,0] + marker_circles[0,1,0])/2
    line_center_y = (marker_circles[0,0,1] + marker_circles[0,1,1])/2
    return line_center_x, line_center_y

def image_processing(image_address):
    print(f"image add = {image_address}")
    cycle = image_address.split("/")[-1].split(".")[0].split("-")[-1]
    image_address_parent_dir = image_address.rsplit('/', 1)[0]
    img_cycle_0_address = f"{image_address_parent_dir}/cycle-0.jpeg"
    img_cycle_0 = cv2.imread(img_cycle_0_address)
    # open relative microtube well coords 
    micro_tube_relative_coords = np.loadtxt("micro_tube_circles_relative.txt", delimiter=" ")
    # find the markers in the cycle-0 image
    marker_center_point = marker_locater(img_cycle_0_address)
    # determine the position of the microtube wells
    new_microwells = micro_tube_relative_coords[:, :2] + marker_center_point
    new_microwells = np.uint16(np.around(new_microwells))
    # centers = np.loadtxt("sorted_centers.csv", delimiter = ",")
    img_cycle = cv2.imread(image_address)
    img = cv2.subtract(img_cycle, img_cycle_0)
    # img = img[410:2285, 800:3330]
    intensity_df_columns = [f"tube_{i}" for i in range(1,len(new_microwells)+1)]

#     print(intensity_df_columns)
    intensity_list = []
#     print(f"this is the centers {centers}")
    circle_radius = 100
    for idx, circle in enumerate(new_microwells):
#         print(f"this is the circles {circle}")
        tube_name = f"tube_{idx+1}"
        circle_center = (int(circle[0]), int(circle[1]))
        f_intensity =  circle_intensity(*circle_center, circle_radius, img)
        intensity_list.append(f_intensity)
        cv2.circle(img, circle_center, circle_radius, (0, 0, 255), 10)
        cv2.imwrite(f"{image_address_parent_dir}/c_{cycle}.jpeg", img)
#         intensity_dict.extend([{"tube_{idx+1}":f_intensity}])
#         print
#         with open("intensities.csv", 'a') as csvfile:
#             writer = csv.DictWriter(csvfile, fieldnames = intensity_df_columns)
#             writer.writeheader()
#             for data in intensity_dict:
#                 writer.writerow(data)
#     print(f"this is cycle intensity_list line 55 {intensity_list}")
    return intensity_list
    
class Worker(QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)
    def __init__(self, iter, out_address, intensity_master_list):
        super().__init__()
        self.iter = iter # cycle number to write as the output image name
        self.out_address = out_address # directory set by user to save data
        self.intensity_master_list = intensity_master_list
        
    def run(self):
        """ Image Capture and Processor worker"""
        dir_path = os.path.join("/home/pi/pcr_app/src", f"{self.out_address}")
        if not os.path.exists(dir_path):
                os.mkdir(dir_path)
        #os.system(f"libcamera-still --nopreview -o {datetimeOBJ.year}-{datetimeOBJ.month}-{datetimeOBJ.day}/{datetimeOBJ.hour}-{datetimeOBJ.minute}-{datetimeOBJ.second}-{self.iter}.jpeg --shutter 6000000 --gain 1 --awbgains 1,1 --immediate")
        img_address = f"/home/pi/pcr_app/src/{self.out_address}/cycle-{self.iter}.jpeg"
        os.system(f"libcamera-still --nopreview -o {img_address} --shutter 6000000 --gain 1 --awbgains 1,1 --immediate")
        print(self.iter)
        # Calling the realtime image processing function
        print("Going to process the image")
        global intensity_list
        intensity_list = image_processing(img_address)
        # print(f"this is the intensity list {intensity_list}")
        # self.intensity_master_list = intensity_list
        f_intensity[str(self.iter)] = intensity_list
#         img = cv2.imread(f"{img_address}.jpeg", cv2.IMREAD_GRAYSCALE)
#         cv2.imwrite(img_address_out, img)
        print("Image Captured and Processed")
        self.finished.emit()

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
f_intensity = pd.DataFrame([0]*45)
class Ui(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):        
        super(Ui, self).__init__(*args, **kwargs)
        # Loading the UI from the .ui file
        uic.loadUi('../ui_files/mainwindow.ui', self)
        # Reading the Assay name set by the user.
        self.lineEdit.setText("Test")
        self.btn_save.clicked.connect(self.btn_save_func)
        self.btn_cancel.clicked.connect(app.instance().quit)
        self.intensity_master_list = [0]*45
        # Plot Style
        self.graph_cycle.setLabel('left', 'Temperature', units='C')
        self.graph_cycle.setLabel('bottom', 'Time')
        self.graph_cycle.setTitle('Cycling Graph')
        #self.graph_cycle.setYRange(55, 100, padding=0)
        self.graph_cycle.setBackground('w')
        self.graph_cycle.showGrid(x=True, y=True)
        # graph_ac plotting graph
        self.graph_ac.setLabel('left', 'Intensity', units='a.u.')
        self.graph_ac.setLabel('bottom', 'Cycle')
        self.graph_ac.setTitle('Amplification Curve')
        self.graph_ac.setBackground('w')
        self.graph_ac.showGrid(x=True, y=True)
        self.graph_ac.addLegend()

        # Ploting the Temprature for 1000 steps of time
        self.temp = [0]*1000
        self.time = [0]*1000
        self.cycle = np.zeros
        self.f_intensity = pd.DataFrame()
        self.dt = 1000 # ms
        pen = pyqtgraph.mkPen(color=(255, 0, 0))
        # list of pens with 45 colors
        self.pens = [pyqtgraph.mkPen(color=(i, 45*1.3), width = 1) for i in range(45)]

        self.plot_ref = self.graph_cycle.plot(self.temp, self.time, pen=pen)
        self.ac_plot_ref = []
        for i in range(45):
            self.ac_plot_ref.append(self.graph_ac.plot(pen = self.pens[i], name = f"Tube {i+1}"))
        self.tab_main.setCurrentIndex(0)
        self.btn_start.clicked.connect(self.send_command)
        self.show()

    def aggregate_params(self):
        # This function is used to set cycle parameters such as time and tempratures
        pred_time = self.spin_time_pred.value()
        pred_temp = self.spin_temp_pred.value()
        den_time = self.spin_time_den.value()
        den_temp = self.spin_temp_den.value()
        ext_temp = self.spin_temp_ext.value()
        ext_time = self.spin_time_ext.value()
        ann_time = self.spin_time_ann.value()
        ann_temp = self.spin_temp_ann.value()
        print(f"cycle_params:{pred_time, pred_temp, den_time, den_temp, ext_temp, ext_time, ann_temp, ann_time}")
        return pred_time, pred_temp, den_time, den_temp, ext_temp, ext_time, ann_temp, ann_time

    def send_command(self):
        # Reseting the buffer to read from the end of the buffer
        ser.reset_input_buffer()
        pred_time, pred_temp, den_time, den_temp, ext_temp, ext_time, ann_temp, ann_time = self.aggregate_params()
        # params_str = f"{pred_time},{pred_temp},{den_time},{den_temp},{ext_time},{ext_temp},{ann_time},{ann_temp}>"
        params_str = f"{pred_time},{pred_temp},{den_time}"
        ser.write(bytes(str(params_str), 'utf-8'))
        # Starting the timer used for realtime plotting of the temprature
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.dt)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        # Printing the read params from arduino
        print(ser.readline() )

    def read_serial(self):
        while True:
            ser.flushInput()
            read = ser.readline().decode('utf-8').rstrip()
            print(read)
    
    def btn_save_func(self):
        dir_path = os.path.join("/home/pi/pcr_app/src", f"{self.lineEdit.text()}")
        if not os.path.exists(dir_path):
                os.mkdir(dir_path)

    def read_data(self, line):
        logging.info(line)
        args = line.split("-")
        logging.info(args)
        
        try:
            current_temp = args[2]
            cycle_number = args[-1][:-1]
            state = args[0]
        except:
            print("Missing")
            logging.info("MISS")
            current_temp = self.temp[-1]
            cycle_number = 99
            state = "*"
        # Debugging Info
        #print(f" current_temp datatype:{type(current_temp)}, current temp {current_temp}")
        #print(state)
        #print(r'{}'.format(state))
        if state=="&#":
            # Here if the cycle state changes to # from * a thread will start to capture image and process it later
            print("TRIGGER!")
            print(args)
            self.thread = QThread(parent = self)
            print(f"iter = {cycle_number}")
            self.worker = Worker(cycle_number, self.lineEdit.text(), self.intensity_master_list)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()
            # self.f_intensity[str(cycle_number)] = self.intensity_master_list
#             self.f_intensity = np.c_[self.f_intensity, self.intensity_master_list]
            try:
                print(f"f_intensity shape is {f_intensity.shape}")
                print(f_intensity.head())
            except:
                print("problem in df")
#             intensity_file = open(f'{self.lineEdit.text()}/intensity.csv', 'w', newline = '')
#             self.intensity_master_list = self.intensity_master_list[-1]
#             print(f"*** {self.intensity_master_list[-1]}")
#             with intensity_file:
#                 write = csv.writer(intensity_file)
#                 write.writerows(self.intensity_master_list)
#             print(f"### {self.intensity_master_list}")
#         print(self.intensity_master_list)
        #try:
        #    print(float(current_temp))
        #except:
        #    logging.info("READ1")
        #        
        #    logging.info(self.temp)
        #    current_temp = self.temp[-1]

        return float(current_temp)

    def update_plot_data(self):
        # self.time = self.time[1:]  # Remove the first y element.
        self.time.append(self.time[-1] +1)  # Add a new value 1 higher than the last.
        # self.temp = self.temp[1:]  # Remove the first
#         self.f_intensity = self.f_intensity[1:]
        try:
            in_read = ser.readline().decode('utf-8').rstrip()
            # A check to only accept full messages
            if in_read[0] == "&" and in_read[-1] == "&":
                self.temp.append(self.read_data(in_read)) # Add a new random value.
            else:
                print("read error 2")
                logging.info("READ2")
                logging.info(self.temp)
                self.temp.append(self.temp[-1])
        except Exception as e:
            print(in_read)
            print(e)
            print("EXCEPT")
            logging.info(e)
            sys.exit(1)
        self.plot_ref.setData(self.time, self.temp)  # Update the data.
        # plot each row of the f_intensity dataframe
        for idx, plot_ref in enumerate(self.ac_plot_ref):
            plot_ref.setData(f_intensity.iloc[idx])
            # plot the plot_ref index on it
            # plot_ref.setLabel('left', f"Intensity {idx}")
        #self.plot_ref2.setData(self.time, self.f_intensity.iloc[:,1])
        #self.plot_ref2.setData(self.time, self.f_intensity.iloc[:,2])

#         self.ac_plot_ref.setData(self.cycle, self.f_intensity[:, -1])

if __name__ == "__main__":
    # To save the log files, setting the name as the exact date time
    log_stamp = datetime.now()
    log_file_name = log_stamp.now()
    logging.basicConfig(filename = f"logs/{log_file_name}.log", filemode='w', format='%(levelname)s - %(message)s', level=logging.INFO)
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
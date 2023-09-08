
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QDialog, QSplitter
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QDialog, QSplitter, QSizePolicy
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QPixmap
import yaml
import os
import time, sys
import subprocess

class FirstWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setupUi(self)
        self.setWindowTitle('MJO Teleconnections Diagnostics')
        self.setGeometry(0, 0, 800, 400)  # Set window position and size
        self.showMaximized()

        #Create the weather image widget
        weather_image = QLabel(self)
        pixmap = QPixmap('weather.jpg') 

        #Replace with the actual path to your weather image file
        #Scale the pixmap to fit the size of the QLabel
        #pixmap = pixmap.scaled(weather_image.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        weather_image.setPixmap(pixmap)
        weather_image.resize(pixmap.width(),pixmap.height())
        # Set the size policy of the QLabel to expand and fill the available space
        weather_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Create the text widgets
        weather_image.setAlignment(Qt.AlignCenter)
        welcome_label = QLabel('Welcome to MJO Teleconnections Diagnostics', self)
        welcome_label.setAlignment(Qt.AlignCenter)
        
        welcome_label.setStyleSheet("border: 1px solid black;font-size: 20px;")
        
        
        button2 = QPushButton('Start', self)
        button2.setFixedSize(70,30)
        #button2.setGeometry(200, 150, 40, 40)
        button2.clicked.connect(self.open_second_window)
        button2.setStyleSheet("border: 1px solid black;font-size: 15px;")
       
        
        #Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(welcome_label)
        left_layout.addStretch()
        left_layout.addWidget(weather_image)
        
        widgetB = QWidget()
        left_layout.addStretch()
        
        left_layout.addWidget(button2,alignment=Qt.AlignCenter)
        left_layout.addStretch()

        #Create a layout for the right half (text widgets and button)
        
        


        # Create a central widget to hold the splitter
        central_widget = QWidget()
        
        central_widget.setLayout(left_layout)
        self.setCentralWidget(central_widget)


    


    def open_second_window(self):
        
        
        self.second_window = EntryWindow(self)
        self.second_window.showMaximized()
        self.hide()
    
    def output(self):
        pass


class EntryWindow(QMainWindow):
    def __init__(self,parent):
        super().__init__()
        #self.setupUi(self)
        scroll_bar= QScrollBar(self)
        self.scroll = QScrollArea()
        self.parent=parent
        self.setWindowTitle('MJO Teleconnections Diagnostics')
        self.setGeometry(0, 0, 800, 400)  
        self.showMaximized()

       
        dir_in_ilabel = QLabel('DIR_IN: Please enter the input data directory path',self)
        start_date_ilabel = QLabel('START_DATE: Please enter the start date',self)
        end_date_ilabel = QLabel('END_DATE: Please enter the end date',self)
        legthFor_ilabel = QLabel('Length of the forecats (in days): Please enter the length of the forecats in days',self)
        num_ensm_ilabel = QLabel('Number of ensembles: Please enter the number of ensembles',self)
        num_ini_ilabel = QLabel('Number of initial dates: Please enter the number of initial dates',self)
        ini_dates_ilabel = QLabel('Initial dates: Please enter all the intial dates',self)
        era_ilabel = QLabel('Use ERA_I for validation: Please check this box if ERA_I is used for validation',self)
        imerg_ilabel = QLabel('Use IMERG for validation: Please check this box if IMERG is used for validation',self)

        

        # Create the text widgets
        dir_in_label = QLabel('DIR_IN:', self)
        self.dir_in_text = QLineEdit(self)
        self.dir_in_text.setProperty("mandatoryField", False)
        start_date_label = QLabel('START_DATE:', self)
        self.start_date_text = QLineEdit(self)
        #calendar = QCalendarWidget(self)
        self.era = True
        self.imerg = True
        end_date_label = QLabel('END_DATE:', self)
        self.end_date_text = QLineEdit(self)
        lengthFor = QLabel('Length of the forecasts (in days):', self)
        self.lengthFor_text = QLineEdit(self)
        num_ensm_label = QLabel('Number of ensembles:', self)
        self.num_ensm = QLineEdit(self)
        num_initial_dates = QLabel('Number of initial dates:', self)
        self.initial_dates = QLineEdit(self)

        
        initial_dates = QLabel('Initial dates:', self)
        self.initial_dates_values = QLineEdit(self)
        
        button2 = QPushButton('Next', self)
        button2.setFixedSize(70,30)
        button2.clicked.connect(self.open_second_window)
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #ERA - 1
        era_label = QLabel('Use ERA_I for validation:', self)
        groupbox = QGroupBox()
        vbox = QVBoxLayout()
        groupbox.setLayout(vbox)
        self.era_yes = QRadioButton("Yes")
        self.era_yes.setChecked(True)
        self.era_yes.toggled.connect(self.onERAClicked)
        vbox.addWidget(self.era_yes)
        self.era_no = QRadioButton("No")
        vbox.addWidget(self.era_no)

        

        #IMERG
        imerg_label = QLabel('Use IMERG for validation:', self)
        groupbox2 = QGroupBox()
        vbox = QVBoxLayout()
        groupbox2.setLayout(vbox)
        self.imerg_yes = QRadioButton("Yes")
        self.imerg_yes.setChecked(True)
        #self.imerg_yes.toggled.connect(self.onIMERGClicked)
        vbox.addWidget(self.imerg_yes )
        self.imerg_no = QRadioButton("No")
        vbox.addWidget(self.imerg_no)
        
        

        #Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        help = QLabel('Help:',self)
        
        left_layout.addStretch()
        left_layout.addWidget(help)
        
        left_layout.addWidget(dir_in_ilabel)
        left_layout.addWidget(start_date_ilabel)
        left_layout.addWidget(end_date_ilabel)
        left_layout.addWidget(legthFor_ilabel)
        left_layout.addWidget(num_ensm_ilabel)
        left_layout.addWidget(num_ini_ilabel)
        left_layout.addWidget(ini_dates_ilabel)
        left_layout.addWidget(era_ilabel)
        left_layout.addWidget(imerg_ilabel)
        left_layout.addStretch()
        left_layout.addWidget(back,alignment=Qt.AlignLeft)
        

        #Create a layout for the right half (text widgets and button)
        right_layout = QVBoxLayout()
        right_layout.addWidget(dir_in_label)
        right_layout.addWidget(self.dir_in_text)
        right_layout.addWidget(start_date_label)
        right_layout.addWidget(self.start_date_text)
        right_layout.addWidget(end_date_label)
        right_layout.addWidget(self.end_date_text)
        right_layout.addWidget(lengthFor)
        right_layout.addWidget(self.lengthFor_text)
        right_layout.addWidget(self.end_date_text)
        right_layout.addWidget(num_ensm_label)
        right_layout.addWidget(self.num_ensm)
        right_layout.addWidget(num_initial_dates)
        right_layout.addWidget(self.initial_dates)
        right_layout.addWidget(initial_dates)
        right_layout.addWidget(self.initial_dates_values)
        right_layout.addWidget(era_label)
        right_layout.addWidget(groupbox)
        right_layout.addWidget(imerg_label)
        right_layout.addWidget(groupbox2)
        right_layout.addStretch()
        right_layout.addWidget(button2,alignment=Qt.AlignRight)
        

        # Create a QSplitter to split the window equally
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(QWidget())
        splitter.addWidget(QWidget())
        splitter.setSizes([1, 1])

        # Set the left layout to the first widget of the splitter
        splitter.widget(0).setLayout(left_layout)
        splitter.widget(0).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the right layout to the second widget of the splitter
        splitter.widget(1).setLayout(right_layout)
        splitter.widget(1).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a central widget to hold the splitter
        central_widget = QWidget()
        central_layout = QHBoxLayout()
        central_layout.addWidget(splitter)
        central_widget.setLayout(central_layout)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(central_widget)
        self.setCentralWidget(self.scroll)


    def onERAClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            self.era = True
        else:
            self.era = False

    def onIMERGClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            self.era = True
        else:
            self.era = False


    def open_second_window(self):

        #commenting out the input validation
        
        '''if self.initial_dates.text() == '' or self.initial_dates_values.text() == '' or self.dir_in_text.text() == '' or self.start_date_text.text() == '' or self.end_date_text.text() == '' or self.num_ensm.text() == '':
            msg = QMessageBox()
            msg.setWindowTitle("Enter all values")
            msg.setText("Please enter all values")
            x=msg.exec_()
            return
        
        num_exp = int(self.initial_dates.text())
        num_given = len(list(map(int,self.initial_dates_values.text().split())))
        if num_exp != num_given:
            msg = QMessageBox()
            msg.setWindowTitle("Number of initial dates should match the give number")
            msg.setText("Please enter "+str(num_exp)+" initial dates")
            x=msg.exec_()
            return'''

        dict_file ={}
        dict_file['DIR_IN'] = self.dir_in_text.text()
        dict_file['START_DATE:']= self.start_date_text.text()
        dict_file['END_DATE:']= self.end_date_text.text()
        dict_file['length of forecasts:'] = self.lengthFor_text.text()
        dict_file['Number of ensembles:'] = self.num_ensm.text()
        dict_file['Number of initial dates:']= int(self.initial_dates.text())
        dict_file['Initial dates:' ]= list(map(int,self.initial_dates_values.text().split()))
        #print(type(self.initial_dates_values.text()),' has values ',list(map(int,self.initial_dates_values.text().split())))
     
        
        if self.era:
            dict_file['ERAI:'] = True
        else:
            dict_file['ERAI:'] = False
        if self.imerg:
            dict_file['IMERG:' ]= True
        else:
            dict_file['IMERG:'] = False

        
        self.second_window = SecondWindow(self,self.dir_in_text.text(),self.era,dict_file)
        self.second_window.showMaximized()
        self.hide()
    

    
    def closee(self):
        self.close()
        self.parent.show()


class SecondWindow(QMainWindow):
    def __init__(self,parent,dirin,era,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent=parent
        self.dict_file = dict_file
        self.setWindowTitle('Daily Anomaly and RMM')
        self.setGeometry(0, 0, 800, 400)  # Set window position and size
        self.showMaximized()
        #Create the weather image widget
        weather_image = QLabel(self)
        pixmap = QPixmap('weather.jpg') 
        self.era = era
       
        #Scale the pixmap to fit the size of the QLabel
        #pixmap = pixmap.scaled(weather_image.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        weather_image.setPixmap(pixmap)
        weather_image.resize(pixmap.width(),pixmap.height())
        # Set the size policy of the QLabel to expand and fill the available space
        weather_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Create the text widgets
        
        self.dailyAnomaly=True

        #Daily anomaly
        dailyAnomaly_label = QLabel('Compute daily anomaly:', self)
        groupbox2 = QGroupBox()
        vbox = QVBoxLayout()
        groupbox2.setLayout(vbox)
        self.dailyAnomaly_yes = QRadioButton("Yes")
        self.dailyAnomaly_yes.setChecked(True)
        self.dailyAnomaly_yes.toggled.connect(self.ondailyAnomalyClicked)
        vbox.addWidget(self.dailyAnomaly_yes)
        self.dailyAnomaly_no = QRadioButton("No")
        vbox.addWidget(self.dailyAnomaly_no)

        self.rmm = False
        #RMM Index
        rmm_label = QLabel('Compute RMM Index:', self)
        groupbox = QGroupBox()
        vbox = QVBoxLayout()
        groupbox.setLayout(vbox)
        self.rmm_yes = QRadioButton("Yes")
        
        self.rmm_yes.toggled.connect(self.onrmmClicked)
        vbox.addWidget(self.rmm_yes)
        self.rmm_no = QRadioButton("No")
        self.rmm_no.setChecked(True)
        vbox.addWidget(self.rmm_no)
       
        self.dirin=dirin
        but = QPushButton('Next', self)
        but.setFixedSize(70,30)
        but.clicked.connect(self.openThirdWindow)

        

        self.dirin = dirin
        prefix = self.dirin+"/OBS/"
        print(prefix)
        #change labels correctly.
        dir_in_label = QLabel('Path to OLR data files:', self)
        self.olrDataFiles = QLineEdit(self)
        self.olrDataFiles.setText(prefix)
        self.olrDataFiles.setCursorPosition(len(prefix))

        zonalpath = QLabel('Path to zonal wind at 850 hPa data files:', self)
        self.zonalpathT  = QLineEdit(self)
        
        self.zonalpathT.setText(prefix)
        self.zonalpathT.setCursorPosition(len(prefix))
        

        zonalpath200 = QLabel('Path to zonal wind at 200 hPa data files:', self)
        self.zonalpath200T = QLineEdit(self)
        self.zonalpath200T.setText(prefix)
        self.zonalpath200T.setCursorPosition(len(prefix))

        but = QPushButton('Submit', self)
        but.setFixedSize(70,30)
        but.clicked.connect(self.openThirdWindow)

        self.groupbox = QGroupBox()
        vbox = QVBoxLayout()
        self.groupbox.setLayout(vbox)
        vbox.addWidget(dir_in_label)
        vbox.addWidget(self.olrDataFiles)
        vbox.addWidget(zonalpath)
        vbox.addWidget(self.zonalpathT)
        vbox.addWidget(zonalpath200)
        vbox.addWidget(self.zonalpath200T)
        vbox.addWidget(but)

        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)

        # Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        left_layout.addWidget(weather_image)
        left_layout.addStretch()
        left_layout.addWidget(back,alignment=Qt.AlignLeft)
        

        # Create a layout for the right half (text widgets and button)
        self.right_layout = QVBoxLayout()
        
        self.right_layout.addWidget(dailyAnomaly_label)
        self.right_layout.addWidget(groupbox2)
        self.right_layout.addWidget(rmm_label)
        self.right_layout.addWidget(groupbox)
        self.right_layout.addStretch()
        self.right_layout.addWidget(but,alignment=Qt.AlignRight)
        
        

        # Create a QSplitter to split the window equally
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(QWidget())
        splitter.addWidget(QWidget())
        splitter.setSizes([1, 1])

        # Set the left layout to the first widget of the splitter
        splitter.widget(0).setLayout(left_layout)
        splitter.widget(0).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the right layout to the second widget of the splitter
        splitter.widget(1).setLayout(self.right_layout)
        splitter.widget(1).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a central widget to hold the splitter
        central_widget = QWidget()
        central_layout = QHBoxLayout()
        central_layout.addWidget(splitter)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def ondailyAnomalyClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            self.dailyAnomaly = True
        else:
            self.dailyAnomaly = False
    def closee(self):
        self.close()
        self.parent.show()
        
        
    
    def onrmmClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            self.rmm = True
            self.right_layout.addWidget(self.groupbox)
            self.right_layout.addStretch()
        else:
            self.rmm = False
            self.groupbox.setParent(None)


    def openThirdWindow(self):
        dict_file=self.dict_file
        if self.dailyAnomaly:
            dict_file['Daily Anomaly:'] = True
        else:
            dict_file['Daily Anomaly:'] = False
        if self.rmm:
            dict_file['RMM:'] = True
        else:
            dict_file['RMM:'] = False
        dict_file['Path to OLR data files:'] = self.olrDataFiles.text()
        dict_file['Path to zonal wind at 850 hPa data files:'] = self.zonalpathT.text()
        dict_file['Path to zonal wind at 200 hPa data files:'] = self.zonalpath200T.text()

        
        self.third_window = ThirdWindow(self,self.dirin,self.era,dict_file)
        self.third_window.showMaximized()
        self.hide()
        
        #self.close()

    def method(self,checked):
        # printing the checked status
        if checked:
            self.right_layout.addWidget(self.groupbox)
            #self.right_layout.addStretch()
            
        else:
            self.groupbox.setParent(None)
            #self.close()




class ThirdWindow(QMainWindow):
    def __init__(self,parent,dirin,era,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent=parent
        self.dict_file = dict_file
        self.setWindowTitle('Third Window')
        self.setGeometry(0, 0, 800, 400)  # Set window position and size
        self.showMaximized()
        # Create the weather image widget
        weather_image = QLabel(self)
        pixmap = QPixmap('weather.jpg') 
        
        #Replace with the actual path to your weather image file
        #Scale the pixmap to fit the size of the QLabel
        #pixmap = pixmap.scaled(weather_image.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        weather_image.setPixmap(pixmap)
        weather_image.resize(pixmap.width(),pixmap.height())
        # Set the size policy of the QLabel to expand and fill the available space
        weather_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Create the text widgets
        
        self.dirin = dirin
        self.era=era
        
        self.all = QCheckBox("Select All")
        self.all.setChecked(False)
        self.all.stateChanged.connect(self.method)

        self.first = QCheckBox("STRIPE Index for geopotential height")
        self.first.setChecked(False)

        self.second = QCheckBox("STRIPE Index for precipitation")
        self.second.setChecked(False)

        self.third = QCheckBox("Pattern CC over the PNA region")
        self.third.setChecked(False)

        self.third_2 = QCheckBox("Pattern CC over the Euro-Atlantic sector")
        self.third_2.setChecked(False) #11

        self.fourth = QCheckBox("Fraction of the observed STRIPE index for geopotential height")
        self.fourth.setChecked(False)

        self.fifth = QCheckBox("Relative amplitude over PNA?")
        self.fifth.setChecked(False)

        self.sixth = QCheckBox("Stratospheric pathway")
        self.sixth.setChecked(False)

        self.seventh = QCheckBox("Histogram of 10 hPa zonal wind")
        self.seventh.setChecked(False)

        self.eight = QCheckBox("Extratropical cyclone activity")
        self.eight.setChecked(False)

        self.nine = QCheckBox("EKE850-Z500 correlation")
        self.nine.setChecked(False)

        self.nine_two = QCheckBox("MJO")
        self.nine_two.setChecked(False) #12

        self.ten = QCheckBox("Surface air temperature")
        self.ten.setChecked(False)

        # Create the checkboxs
        but = QPushButton('Submit', self)
        but.setFixedSize(70,30)
        but.clicked.connect(self.openThirdSubWindow)
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        
        # Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        left_layout.addWidget(weather_image)
        left_layout.addStretch()
        left_layout.addWidget(back,alignment=Qt.AlignLeft)
        

        # Create a layout for the right half (text widgets and button)
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.all)
        right_layout.addWidget(self.first)
        right_layout.addWidget(self.second)
        right_layout.addWidget(self.third)
        right_layout.addWidget(self.third_2)
        right_layout.addWidget(self.fourth)
        right_layout.addWidget(self.fifth)
        right_layout.addWidget(self.sixth)
        right_layout.addWidget(self.seventh)
        right_layout.addWidget(self.eight)
        right_layout.addWidget(self.nine)
        right_layout.addWidget(self.nine_two)
        right_layout.addWidget(self.ten)
        right_layout.addStretch()
        right_layout.addWidget(but,alignment=Qt.AlignRight)
        

        # Create a QSplitter to split the window equally
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(QWidget())
        splitter.addWidget(QWidget())
        splitter.setSizes([1, 1])

        # Set the left layout to the first widget of the splitter
        splitter.widget(0).setLayout(left_layout)
        splitter.widget(0).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the right layout to the second widget of the splitter
        splitter.widget(1).setLayout(right_layout)
        splitter.widget(1).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a central widget to hold the splitter
        central_widget = QWidget()
        central_layout = QHBoxLayout()
        central_layout.addWidget(splitter)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)
    def closee(self):
        self.close()
        self.parent.show()
    def openThirdSubWindow(self):
        selected=[]
        if(self.all.isChecked()):
            selected.append(0)
        else:
            if self.first.isChecked():
                selected.append(1)
            if self.second.isChecked():
                selected.append(2)
            if self.third.isChecked():
                selected.append(3)
            if self.third_2.isChecked():
                selected.append(11)
            if self.fourth.isChecked():
                selected.append(4)
            if self.fifth.isChecked():
                selected.append(5)
            if self.sixth.isChecked():
                selected.append(6)
            if self.seventh.isChecked():
                selected.append(7)
            if self.eight.isChecked():
                selected.append(8)
            if self.nine.isChecked():
                selected.append(9)
            if self.nine_two.isChecked():
                selected.append(12)
            if self.ten.isChecked():
                selected.append(10)
        if selected == []:
            msg = QMessageBox()
            msg.setWindowTitle("Empty input given")
            msg.setText("Please choose the calculations you want to perform")
            x=msg.exec_()
            return
        self.ThirdSubWindow = ThirdSubWindow(self,selected,self.dirin,self.era,self.dict_file)
        self.ThirdSubWindow.showMaximized()
        self.hide()
        
        #self.close()
    
    

    def method(self,checked):
        # printing the checked status
        if checked:
            self.all.setChecked(True)
            self.first.setChecked(True)
            self.second.setChecked(True)
            self.third.setChecked(True)
            self.third_2.setChecked(True)
            self.fourth.setChecked(True)
            self.fifth.setChecked(True)
            self.sixth.setChecked(True)
            self.seventh.setChecked(True)
            self.eight.setChecked(True)
            self.nine.setChecked(True)
            self.nine_two.setChecked(True)
            self.ten.setChecked(True)
        else:
            self.all.setChecked(False)
            self.first.setChecked(False)
            self.second.setChecked(False)
            self.third.setChecked(False)
            self.third_2.setChecked(False)
            self.fourth.setChecked(False)
            self.fifth.setChecked(False)
            self.sixth.setChecked(False)
            self.seventh.setChecked(False)
            self.eight.setChecked(False)
            self.nine.setChecked(False)
            self.nine_two.setChecked(False)
            self.ten.setChecked(False)

 
        


class ThirdSubWindow(QMainWindow):
    def __init__(self,parent,selected,dirin,era,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent=parent
        self.selected = selected
        self.dict_file = dict_file
        vbox = QHBoxLayout()
        self.setWindowTitle('Third Sub Window')
        self.setGeometry(0, 0, 800, 400)  # Set window position and size
        self.showMaximized()
        scroll_bar = QScrollBar(self)
        # Create the weather image widget
        weather_image = QLabel(self)
        pixmap = QPixmap('weather.jpg') 
        
        #Replace with the actual path to your weather image file
        #Scale the pixmap to fit the size of the QLabel
        #pixmap = pixmap.scaled(weather_image.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        weather_image.setPixmap(pixmap)
        weather_image.resize(pixmap.width(),pixmap.height())
        # Set the size policy of the QLabel to expand and fill the available space
        weather_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Create the text widgets
        
        self.dirin = dirin
        pref = self.dirin+"/"
        prefix = self.dirin+"/OBS/"
        
        #change labels correctly.

        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        right_layout = QVBoxLayout(self)

        num_dates = dict_file['Number of initial dates:']
        dates = dict_file['Initial dates:' ]
        print(dates)
        print(num_dates)

        self.num_dates = num_dates
        # Path to Z500 data files:
        z500s=[]
        self.z500Ts = []
        
        self.z500Tobss = []

        for i in range(num_dates):
            z500 = QLabel(f'Path to Z500 model data files for date {dates[i]}:', self)
            self.z500T = QLineEdit(self)
            self.z500T.setText(pref)
            self.z500T.setCursorPosition(len(pref))

            z500s.append(z500)
            self.z500Ts.append(self.z500T)
         
        
        z500obs = QLabel(f'Path to Z500 observational data files:', self)
        self.z500Tobs = QLineEdit(self)
        self.z500Tobs.setText(prefix)
        self.z500Tobs.setCursorPosition(len(prefix))

        dir_OLR_label = QLabel('Path to OLR data files:', self)
        self.olrDataFiles = QLineEdit(self)
        self.olrDataFiles.setText(prefix)
        self.olrDataFiles.setCursorPosition(len(prefix))


        # Path to Z100 data files:
        z100s = []
        self.z100Ts = []
        
        self.z100Tobss = []
    
        for i in range(num_dates):
            z100 = QLabel(f'Path to Z100 model data files for date {dates[i]}:', self)
            self.z100T = QLineEdit(self)
            self.z100T.setText(pref)
            self.z100T.setCursorPosition(len(pref))


            z100s.append(z100)
            self.z100Ts.append(self.z100T)
            
        z100obs = QLabel(f'Path to Z100 observational data files:', self)
        self.z100Tobs = QLineEdit(self)
        self.z100Tobs.setText(prefix)
        self.z100Tobs.setCursorPosition(len(prefix))



        # Path to zonal wind at 850 hPa data files:
        zonalwind850s = []
        self.zonalwind850Ts = []
        
        self.zonalwind850Tobss = []

        for i in range(num_dates):
            zonalwind850 = QLabel(f'Path to zonal wind at 850 hPa model data files for date {dates[i]}:', self)
            self.zonalwind850T = QLineEdit(self)
            self.zonalwind850T.setText(pref)
            self.zonalwind850T.setCursorPosition(len(pref))

            

            zonalwind850s.append(zonalwind850)
            self.zonalwind850Ts.append(self.zonalwind850T)
            
        zonalwind850obs = QLabel(f'Path to zonal wind at 850 hPa observational data files:', self)
        self.zonalwind850Tobs = QLineEdit(self)
        self.zonalwind850Tobs.setText(prefix)
        self.zonalwind850Tobs.setCursorPosition(len(prefix))

        # Path to zonal wind at 200 hPa data files:
        zonalwind200s = []
        self.zonalwind200Ts = []
        
        self.zonalwind200Tobss = []

        for i in range(num_dates):
            zonalwind200 = QLabel(f'Path to zonal wind at 200 hPa model data files for date {dates[i]}:', self)
            self.zonalwind200T = QLineEdit(self)
            self.zonalwind200T.setText(pref)
            self.zonalwind200T.setCursorPosition(len(pref))

            

            zonalwind200s.append(zonalwind200)
            self.zonalwind200Ts.append(self.zonalwind200T)
            
        zonalwind200obs = QLabel(f'Path to zonal wind at 200 hPa observational data files:', self)
        self.zonalwind200Tobs = QLineEdit(self)
        self.zonalwind200Tobs.setText(prefix)
        self.zonalwind200Tobs.setCursorPosition(len(prefix))



        # Path to zonal wind at 10 hPa data files:
        zonalwind10s = []
        self.zonalwind10Ts = []
        zonalwind10obss = []
        self.zonalwind10Tobss = []
        for i in range(num_dates):
            zonalwind10 = QLabel(f'Path to zonal wind at 10 hPa model data files for date {dates[i]}:', self)
            self.zonalwind10T = QLineEdit(self)
            self.zonalwind10T.setText(pref)
            self.zonalwind10T.setCursorPosition(len(pref))

            

            zonalwind10s.append(zonalwind10)
            self.zonalwind10Ts.append(self.zonalwind10T)
            
        zonalwind10obs = QLabel(f'Path to zonal wind at 10 hPa observational data files:', self)
        self.zonalwind10Tobs = QLineEdit(self)
        self.zonalwind10Tobs.setText(prefix)
        self.zonalwind10Tobs.setCursorPosition(len(prefix))



        # Path to meridional wind at 850 hPa data files:
        meridionalwind850s =[]
        self.meridionalwind850Ts = []
        meridionalwind850obss = []
        self.meridionalwind850Tobss = []

        for i in range(num_dates):
            meridionalwind850 = QLabel(f'Path to meridional wind at 850 hPa model data files for date {dates[i]}:', self)
            self.meridionalwind850T = QLineEdit(self)
            self.meridionalwind850T.setText(pref)
            self.meridionalwind850T.setCursorPosition(len(pref))

            meridionalwind850s.append(meridionalwind850)
            self.meridionalwind850Ts.append(self.meridionalwind850T)
                    
        meridionalwind850obs = QLabel(f'Path to meridional wind at 850 hPa observational data files:', self)
        self.meridionalwind850Tobs = QLineEdit(self)
        self.meridionalwind850Tobs.setText(prefix)
        self.meridionalwind850Tobs.setCursorPosition(len(prefix))


        # Path to meridional wind at 500 hPa data files:

        meridionalwind500s = []
        self.meridionalwind500Ts = []
        meridionalwind500obss = []
        self.meridionalwind500Tobss = []

        for i in range(num_dates):
            meridionalwind500 = QLabel(f'Path to meridional wind at 500 hPa model data files for date {dates[i]}:', self)
            self.meridionalwind500T = QLineEdit(self)
            self.meridionalwind500T.setText(pref)
            self.meridionalwind500T.setCursorPosition(len(pref))

            meridionalwind500s.append(meridionalwind500)
            self.meridionalwind500Ts.append(self.meridionalwind500T)
        meridionalwind500obs = QLabel(f'Path to meridional wind at 500 hPa observational data files:', self)
        self.meridionalwind500Tobs = QLineEdit(self)
        self.meridionalwind500Tobs.setText(prefix)
        self.meridionalwind500Tobs.setCursorPosition(len(prefix))

        # Path to temperature at 500 hPa data files:
        temperature500s = []
        self.temperature500Ts = []
        temperature500obss = []
        self.temperature500Tobss = []

        for i in range(num_dates):
            temperature500 = QLabel(f'Path to temperature at 500 hPa model data files for date {dates[i]}:', self)
            self.temperature500T = QLineEdit(self)
            self.temperature500T.setText(pref)
            self.temperature500T.setCursorPosition(len(pref))

            

            temperature500s.append(temperature500)
            self.temperature500Ts.append(self.temperature500T)
            
        temperature500obs = QLabel(f'Path to temperature at 500 hPa observational data files:', self)
        self.temperature500Tobs = QLineEdit(self)
        self.temperature500Tobs.setText(prefix)
        self.temperature500Tobs.setCursorPosition(len(prefix))


        # Path to T2m data files:
        t2ms = []
        self.t2mTs = []
        t2mobss = []
        self.t2mTobss = []
        for i in range(num_dates):
            t2m = QLabel(f'Path to T2m model data files for date {dates[i]}:', self)
            self.t2mT = QLineEdit(self)
            self.t2mT.setText(pref)
            self.t2mT.setCursorPosition(len(pref))

            t2ms.append(t2m)
            self.t2mTs.append(self.t2mT)
        t2mobs = QLabel(f'Path to T2m observational data files:', self)
        self.t2mTobs = QLineEdit(self)
        self.t2mTobs.setText(prefix)
        self.t2mTobs.setCursorPosition(len(prefix))




        # Path to precipitational data files:
        precDatas = []
        self.precDataTs = []
        precDataobss = []
        self.precDataTobss = []

        for i in range(num_dates):
            precData = QLabel(f'Path to precipitation model data files for date {dates[i]}:', self)
            self.precDataT = QLineEdit(self)
            self.precDataT.setText(pref)
            self.precDataT.setCursorPosition(len(pref))

            precDatas.append(precData)
            self.precDataTs.append(self.precDataT)
        precDataobs = QLabel(f'Path to precipitation observational data files:', self)
        self.precDataTobs = QLineEdit(self)
        self.precDataTobs.setText(prefix)
        self.precDataTobs.setCursorPosition(len(prefix))
            


        weeks = QLabel('Select weeks:', self)
        self.selectweeks = QLineEdit(self)

        #Compute the of Z500 anomalies
        self.z500anomalies = QCheckBox("Compute the z500 anomalies")
        self.z500anomalies.setChecked(False)

        self.dailyMean= QCheckBox("Model input file daily mean?")
        self.dailyMean.setChecked(False)

        but = QPushButton('Submit', self)
        but.setFixedSize(70,30)
        but.clicked.connect(self.submi)
        
        rendered=[]
        if(len(selected)>=1):
            if (selected[0]==0):
                rendered.append('z500T')
                for i in range(num_dates):
                    right_layout.addWidget(z500s[i])
                    right_layout.addWidget(self.z500Ts[i])
                if era == False:
                    right_layout.addWidget(z500obs)
                    right_layout.addWidget(self.z500Tobs)

                rendered.append('z100T')
                for i in range(num_dates):
                    right_layout.addWidget(z100s[i])
                    right_layout.addWidget(self.z100Ts[i])
                if era == False:
                    right_layout.addWidget(z100obs)
                    right_layout.addWidget(self.z100Tobs)

                rendered.append('zonalwind850T')
                for i in range(num_dates):
                    right_layout.addWidget(zonalwind850s[i])
                    right_layout.addWidget(self.zonalwind850Ts[i])
                if era == False:
                    right_layout.addWidget(zonalwind850obs)
                    right_layout.addWidget(self.zonalwind850Tobs)

                rendered.append('meridionalwind850T')
                for i in range(num_dates):
                    right_layout.addWidget(meridionalwind850s[i])
                    right_layout.addWidget(self.meridionalwind850Ts[i])
                if era == False:
                    right_layout.addWidget(meridionalwind850obs)
                    right_layout.addWidget(self.meridionalwind850Tobs)
                
                rendered.append('dirOLR')
                right_layout.addWidget(dir_OLR_label)
                right_layout.addWidget(self.olrDataFiles)

                rendered.append('meridionalwind500T')
                for i in range(num_dates):
                    right_layout.addWidget(meridionalwind500s[i])
                    right_layout.addWidget(self.meridionalwind500Ts[i])
                if era == False:
                    right_layout.addWidget(meridionalwind500obs)
                    right_layout.addWidget(self.meridionalwind500Tobs)

                rendered.append('zonalwind10T')
                for i in range(num_dates):
                    right_layout.addWidget(zonalwind10s[i])
                    right_layout.addWidget(self.zonalwind10Ts[i])
                if era == False:
                    right_layout.addWidget(zonalwind10obs)
                    right_layout.addWidget(self.zonalwind10Tobs)

                rendered.append('zonalwind200T')
                for i in range(num_dates):
                    right_layout.addWidget(zonalwind200s[i])
                    right_layout.addWidget(self.zonalwind200Ts[i])
                if era == False:
                    right_layout.addWidget(zonalwind200obs)
                    right_layout.addWidget(self.zonalwind200Tobs)

                rendered.append('temperature500T')
                for i in range(num_dates):
                    right_layout.addWidget(temperature500s[i])
                    right_layout.addWidget(self.temperature500Ts[i])
                if era == False:
                    right_layout.addWidget(temperature500obs)
                    right_layout.addWidget(self.temperature500Tobs)


                rendered.append('t2mT')
                for i in range(num_dates):
                    right_layout.addWidget(t2ms[i])
                    right_layout.addWidget(self.t2mTs[i])
                if era == False:
                    right_layout.addWidget(t2mobs)
                    right_layout.addWidget(self.t2mTobs)

                rendered.append('precDataT')
                for i in range(num_dates):
                    right_layout.addWidget(precDatas[i])
                    right_layout.addWidget(self.precDataTs[i])
                if era == False:
                    right_layout.addWidget(precDataobs)
                    right_layout.addWidget(self.precDataTobs)

            else:
                if 1 in selected:
                    if 'z500T' not in rendered:
                        rendered.append('z500T')
                        for i in range(num_dates):
                            right_layout.addWidget(z500s[i])
                            right_layout.addWidget(self.z500Ts[i])
                        if era == False:
                            right_layout.addWidget(z500obs)
                            right_layout.addWidget(self.z500Tobs)
            
                if 2 in selected:
                    if 'precDataT' not in rendered:
                        rendered.append('precDataT')
                        for i in range(num_dates):
                            right_layout.addWidget(precDatas[i])
                            right_layout.addWidget(self.precDataTs[i])
                        if era == False:
                            right_layout.addWidget(precDataobs)
                            right_layout.addWidget(self.precDataTobs)

                if 3 in selected or 11 in selected: #Fraction of the observed STRIPE
                    if 'z500T' not in rendered:
                        rendered.append('z500T')
                        for i in range(num_dates):
                            right_layout.addWidget(z500s[i])
                            right_layout.addWidget(self.z500Ts[i])
                        if era == False:
                            right_layout.addWidget(z500obs)
                            right_layout.addWidget(self.z500Tobs)

                    right_layout.addWidget(weeks)
                    right_layout.addWidget(self.selectweeks)
            

                    
                if 4 in selected: #Pattern CC over
                    if 'z500T' not in rendered:
                        rendered.append('z500T')
                        for i in range(num_dates):
                            right_layout.addWidget(z500s[i])
                            right_layout.addWidget(self.z500Ts[i])
                        if era == False:
                            right_layout.addWidget(z500obs)
                            right_layout.addWidget(self.z500Tobs)
                    right_layout.addWidget(self.z500anomalies)
                    
            
                
                if 5 in selected: #relative amplitude over PNA
                    if 'z500T' not in rendered:
                        rendered.append('z500T')
                        for i in range(num_dates):
                            right_layout.addWidget(z500s[i])
                            right_layout.addWidget(self.z500Ts[i])
                        if era == False:
                            right_layout.addWidget(z500obs)
                            right_layout.addWidget(self.z500Tobs)
                    
                if 6 in selected:
                    if 'z500T' not in rendered:
                        rendered.append('z500T')
                        for i in range(num_dates):
                            right_layout.addWidget(z500s[i])
                            right_layout.addWidget(self.z500Ts[i])
                        if era == False:
                            right_layout.addWidget(z500obs)
                            right_layout.addWidget(self.z500Tobs)
                    if 'z100T' not in rendered:
                        rendered.append('z100T')
                        for i in range(num_dates):
                            right_layout.addWidget(z100s[i])
                            right_layout.addWidget(self.z100Ts[i])
                        if era == False:
                            right_layout.addWidget(z100obs)
                            right_layout.addWidget(self.z100Tobs)

                    if 'meridionalwind500T' not in rendered:
                        rendered.append('meridionalwind500T')
                        for i in range(num_dates):
                            right_layout.addWidget(meridionalwind500s[i])
                            right_layout.addWidget(self.meridionalwind500Ts[i])
                        if era == False:
                            right_layout.addWidget(meridionalwind500obs)
                            right_layout.addWidget(self.meridionalwind500Tobs)
                    
                    if 'temperature500T' not in rendered:
                        rendered.append('temperature500T')
                        for i in range(num_dates):
                            right_layout.addWidget(temperature500s[i])
                            right_layout.addWidget(self.temperature500Ts[i])
                        if era == False:
                            right_layout.addWidget(temperature500obs)
                            right_layout.addWidget(self.temperature500Tobs)
                    
                    if 'zonalwind10T' not in rendered:
                        rendered.append('zonalwind10T')
                        for i in range(num_dates):
                            right_layout.addWidget(zonalwind10s[i])
                            right_layout.addWidget(self.zonalwind10Ts[i])
                        if era == False:
                            right_layout.addWidget(zonalwind10obs)
                            right_layout.addWidget(self.zonalwind10Tobs)




                    

                if 7 in selected: #histogram of 10hpa zonal wind
                    if 'zonalwind10T' not in rendered:
                        rendered.append('zonalwind10T')
                        for i in range(num_dates):
                            right_layout.addWidget(zonalwind10s[i])
                            right_layout.addWidget(self.zonalwind10Ts[i])
                        if era == False:
                            right_layout.addWidget(zonalwind10obs)
                            right_layout.addWidget(self.zonalwind10Tobs)
                    

                if 8 in selected: #Extratropical cyclone activity
                    rendered.append('dailyMean')
                    right_layout.addWidget(self.dailyMean)
                    if 'zonalwind850T' not in rendered:
                        rendered.append('zonalwind850T')
                        for i in range(num_dates):
                            right_layout.addWidget(zonalwind850s[i])
                            right_layout.addWidget(self.zonalwind850Ts[i])
                        if era == False:
                            right_layout.addWidget(zonalwind850obs)
                            right_layout.addWidget(self.zonalwind850Tobs)
                    
                    if 'meridionalwind850T' not in rendered:
                        rendered.append('meridionalwind850T')
                        for i in range(num_dates):
                            right_layout.addWidget(meridionalwind850s[i])
                            right_layout.addWidget(self.meridionalwind850Ts[i])
                        if era == False:
                            right_layout.addWidget(meridionalwind850obs)
                            right_layout.addWidget(self.meridionalwind850Tobs)
                    
                    if 'z500T' not in rendered:
                        rendered.append('z500T')
                        for i in range(num_dates):
                            right_layout.addWidget(z500s[i])
                            right_layout.addWidget(self.z500Ts[i])
                        if era == False:
                            right_layout.addWidget(z500obs)
                            right_layout.addWidget(self.z500Tobs)
                    


                    
                if 9 in selected: #Surface air temperature
                    if 'dailyMean' not in rendered:
                        rendered.append('dailyMean')
                        right_layout.addWidget(self.dailyMean)
                    if 'zonalwind850T' not in rendered:
                        rendered.append('zonalwind850T')
                        for i in range(num_dates):
                            right_layout.addWidget(zonalwind850s[i])
                            right_layout.addWidget(self.zonalwind850Ts[i])
                        if era == False:
                            right_layout.addWidget(zonalwind850obs)
                            right_layout.addWidget(self.zonalwind850Tobs)
                    if 'meridionalwind850T' not in rendered:
                        rendered.append('meridionalwind850T')
                        for i in range(num_dates):
                            right_layout.addWidget(meridionalwind850s[i])
                            right_layout.addWidget(self.meridionalwind850Ts[i])
                        if era == False:
                            right_layout.addWidget(meridionalwind850obs)
                            right_layout.addWidget(self.meridionalwind850Tobs)
                if 10 in selected:
                    rendered.append('t2mT')
                    for i in range(num_dates):
                        right_layout.addWidget(t2ms[i])
                        right_layout.addWidget(self.t2mTs[i])
                    if era == False:
                        right_layout.addWidget(t2mobs)
                        right_layout.addWidget(self.t2mTobs)
                if 12 in selected:
                    rendered.append('dirOLR') #doesn't have a yaml entry
                    right_layout.addWidget(dir_OLR_label)
                    right_layout.addWidget(self.olrDataFiles)
                    if 'zonalwind850T' not in rendered:
                        rendered.append('zonalwind850T')
                        for i in range(num_dates):
                            right_layout.addWidget(zonalwind850s[i])
                            right_layout.addWidget(self.zonalwind850Ts[i])
                        if era == False:
                            right_layout.addWidget(zonalwind850obs)
                            right_layout.addWidget(self.zonalwind850Tobs)
                    if 'zonalwind200T' not in rendered:
                        rendered.append('zonalwind200T')
                        for i in range(num_dates):
                            right_layout.addWidget(zonalwind200s[i])
                            right_layout.addWidget(self.zonalwind200Ts[i])
                        if era == False:
                            right_layout.addWidget(zonalwind200obs)
                            right_layout.addWidget(self.zonalwind200Tobs)
                

                    
                        

                    
                    

        right_layout.addStretch()
        right_layout.addWidget(but,alignment=Qt.AlignRight)    
        
        
        self.widget.setLayout(right_layout)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)

        # Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        left_layout.addWidget(weather_image)
        left_layout.addStretch()
        left_layout.addWidget(back,alignment=Qt.AlignLeft)
        

        # Create a layout for the right half (text widgets and button)
        

        # Create a QSplitter to split the window equally
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(QWidget())
        splitter.addWidget(QWidget())
        splitter.setSizes([1, 1])

        # Set the left layout to the first widget of the splitter
        splitter.widget(0).setLayout(left_layout)
        splitter.widget(0).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        vbox.addWidget(self.scroll)
        # Set the right layout to the second widget of the splitter
        splitter.widget(1).setLayout(vbox)
        splitter.widget(1).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a central widget to hold the splitter

        central_widget = QWidget()
        central_layout = QHBoxLayout()
        central_layout.addWidget(splitter)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)
    
    def closee(self):
        self.close()
        self.parent.show()
    def submi(self):
        dict_file =self.dict_file
        dict_file['Path to z500 date files'] = []
        for i in self.z500Ts:
            dict_file['Path to z500 date files'].append(i.text())

        dict_file['Path to z500 observational files'] = self.z500Tobs.text()


        
        dict_file['Path to z100 date files'] = []
        for i in self.z100Ts:
            dict_file['Path to z100 date files'].append(i.text())

        dict_file['Path to z100 observational files'] = self.z100Tobs.text()

        
        dict_file['Path to zonalwind850 date files'] = []
        for i in self.zonalwind850Ts:
            dict_file['Path to zonalwind850 date files'].append(i.text())

        dict_file['Path to zonalwind850 observational files'] = self.zonalwind850Tobs.text()

        
        dict_file['Path to meridional wind at 850 hPa date files'] = []
        for i in self.meridionalwind850Ts:
            dict_file['Path to meridional wind at 850 hPa date files'].append(i.text())

        dict_file['Path to meridional wind at 850 hPa observational data file'] = self.meridionalwind850Tobs.text()

        
        dict_file['Path to meridional wind at 500 hPa date files'] = []
        for i in self.meridionalwind500Ts:
            dict_file['Path to meridional wind at 500 hPa date files'].append(i.text())

        dict_file['Path to meridional wind at 500 hPa observational data files:'] = self.meridionalwind500Tobs.text()

        dict_file['Path to zonal wind at 10 hPa data files:'] = []
        for i in self.zonalwind10Ts:
            dict_file['Path to zonal wind at 10 hPa data files:'].append(i.text())
        dict_file['Path to zonal wind at 10 hPa observational data files:'] = self.zonalwind10Tobs.text()

        dict_file['Path to temperature at 500 hPa data files' ]=[]
        for i in self.temperature500Ts:
            dict_file['Path to temperature at 500 hPa data files' ].append(i.text())
        dict_file['Path to temperature at 500 hPa observational data files'] = self.temperature500Tobs.text()

        dict_file['Path to zonal wind at 200 hPa data files:'] = []
        for i in self.zonalwind200Ts:
            dict_file['Path to zonal wind at 200 hPa data files:'].append(i.text())
        dict_file['Path to zonal wind at 200 hPa observational data files:'] = self.zonalwind200Tobs.text()

        
        dict_file['Path to precipitation data files:'] = []
        for i in self.precDataTs:
            dict_file['Path to precipitation data files:'].append(i.text())

        dict_file['Path to precipitation observational data files:'] = self.precDataTobs.text()
        
        dict_file['Select weeks:'] = self.selectweeks.text()

        dict_file['Path to T2m model data files for date'] = []
        for i in self.t2mTs:
            dict_file['Path to T2m model data files for date'].append(i.text())
        dict_file['Path to T2m observational data files:'] = self.t2mTobs.text()
        

        if self.z500anomalies.isChecked():
            dict_file['Compute the z500 anomalies:'] = True
        else:
            dict_file['Compute the z500 anomalies:'] = False
        if self.dailyMean.isChecked():
            dict_file['Model input file daily mean:'] = True
        else:
            dict_file['Model input file daily mean:'] = False
        file = open(r'config.yml', 'w') 
        yaml.dump(dict_file, file)
        file.close()
        self.hide()
        #self.close()
        #run_longtask()
        diagnostics_paths = ["/home/skollapa/MJO-Teleconnections/MJO-Teleconnections/T2m_composites/t2m_composites.py"]
        
        
        with open("/home/skollapa/MJO-Teleconnections/MJO-Teleconnections/T2m_composites/t2m_composites.py") as f:
            exec(f.read())
        

class ProgressBar(QMainWindow):
  
    def __init__(self,parent,dirin,dict_file):
        super().__init__()
        self.setGeometry(200, 200, 500, 300)
        self.showMaximized()
        # calling initUI method
        self.parent = parent
        self.dirin = dirin
        self.dict_file = dict_file
        
        self.initUI()
        
  
    # method for creating widgets
    def initUI(self):
  
        # creating progress bar
        self.pbar = QProgressBar(self)
  
        # setting its geometry
        self.pbar.setGeometry(200, 100, 200, 30)
        self.pbar.setAlignment(Qt.AlignCenter)
        self.setWindowTitle("Calculations in progress")
  
        for i in range(101):
            time.sleep(0.025)
            self.pbar.setValue(i)
            time.sleep(0.025)

        self.hide()
        self.OutputWindow = OutputWindow(self,self.dirin,self.dict_file)
        self.OutputWindow.showMaximized()
        self.close()

class OutputWindow(QMainWindow):
    def __init__(self,parent,dirin,dict_file):
        parent.hide()
        super().__init__()
        #self.setupUi(self)
        
        self.parent = parent
        self.dict_file = dict_file
        #self.setupUi(self)
        scroll_bar = QScrollBar(self)
        self.scroll = QScrollArea() 
        central_widget = QWidget()
        self.setWindowTitle('Results')
        self.setGeometry(0, 0, 800, 400)  # Set window position and size
        self.showMaximized()
        
        glayout = QGridLayout()
        stripes = []
        for i in range(4):
            path = 'OutputImgs/Stripes_'+str(i+1)+'.png'
            px1 = QPixmap(path)
            #px1.setDevicePixelRatio(0.5)
            stripes.append(px1)

        for i in range(4):
            image = QLabel(self)
            image.setPixmap(stripes[i].scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            glayout.addWidget(image,0,i)

        weather_image = QLabel(self)
        pixmap = QPixmap('weather.jpg') 
        central_widget.setLayout(glayout)
        #Replace with the actual path to your weather image file
        #Scale the pixmap to fit the size of the QLabel
        #pixmap = pixmap.scaled(weather_image.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        weather_image.setPixmap(pixmap)
        weather_image.resize(pixmap.width(),pixmap.height())
        # Set the size policy of the QLabel to expand and fill the available space
        #weather_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Create the text widgets

        
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(central_widget)
        #central_widget.setLayout(glayout)
        self.setCentralWidget(self.scroll)
        self.show()
    
    def closee(self):
        self.close()
        self.parent.show()
    
    

    def method(self,checked):
        # printing the checked status
        if checked:
            self.all.setChecked(True)
            self.first.setChecked(True)
            self.second.setChecked(True)
            self.third.setChecked(True)
            self.third_2.setChecked(True)
            self.fourth.setChecked(True)
            self.fifth.setChecked(True)
            self.sixth.setChecked(True)
            self.seventh.setChecked(True)
            self.eight.setChecked(True)
            self.nine.setChecked(True)
            self.nine_two.setChecked(True)
            self.ten.setChecked(True)
        else:
            self.all.setChecked(False)

    def closee(self):
        self.close()
        self.parent.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet('*[mandatoryField="true"] { background-color: yellow }')
    entry_window = FirstWindow()
    entry_window.show()
    sys.exit(app.exec())

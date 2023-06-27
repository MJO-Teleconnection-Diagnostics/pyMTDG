#have to add back buttons
#solve the issue with overflowing layout
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QDialog, QSplitter
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QDialog, QSplitter, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QPixmap
import yaml

class EntryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        dir_in_label = QLabel('DIR_IN:', self)
        self.dir_in_text = QLineEdit(self)

        start_date_label = QLabel('START_DATE:', self)
        self.start_date_text = QLineEdit(self)
        #calendar = QCalendarWidget(self)
        self.era = True
        self.imerg = True
        end_date_label = QLabel('END_DATE:', self)
        self.end_date_text = QLineEdit(self)
        num_ensm_label = QLabel('Number of ensembles:', self)
        self.num_ensm = QLineEdit(self)
        num_initial_dates = QLabel('Number of initial dates:', self)
        self.initial_dates = QLineEdit(self)

        
        button2 = QPushButton('Next', self)
        button2.clicked.connect(self.open_second_window)

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
        imerg_label = QLabel('Use ERA_I for validation:', self)
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
        left_layout.addWidget(weather_image)
        left_layout.addStretch()

        #Create a layout for the right half (text widgets and button)
        right_layout = QVBoxLayout()
        right_layout.addWidget(dir_in_label)
        right_layout.addWidget(self.dir_in_text)
        right_layout.addWidget(start_date_label)
        right_layout.addWidget(self.start_date_text)
        right_layout.addWidget(end_date_label)
        right_layout.addWidget(self.end_date_text)
        right_layout.addWidget(num_ensm_label)
        right_layout.addWidget(self.num_ensm)
        right_layout.addWidget(num_initial_dates)
        right_layout.addWidget(self.initial_dates)
        right_layout.addWidget(era_label)
        right_layout.addWidget(groupbox)
        right_layout.addWidget(imerg_label)
        right_layout.addWidget(groupbox2)
        right_layout.addWidget(button2)
        right_layout.addStretch()

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
        dict_file =[]
        dict_file.append({'DIR_IN' : self.dir_in_text.text()})
        dict_file.append({'START_DATE:' : self.start_date_text.text()})
        dict_file.append({'END_DATE:' : self.end_date_text.text()})
        dict_file.append({'Number of ensembles:' : self.num_ensm.text()})
        dict_file.append({'Number of initial dates:' : self.initial_dates.text()})
        if self.era:
            dict_file.append({'ERAI:' : True})
        else:
            dict_file.append({'ERAI:' : False})
        if self.imerg:
            dict_file.append({'IMERG:' : True})
        else:
            dict_file.append({'IMERG:' : False})

        yaml.dump(dict_file, file)
        self.second_window = SecondWindow(self.dir_in_text.text(),self.era)
        self.second_window.showMaximized()
        #self.close()
    
    def output(self):
        pass


class SecondWindow(QMainWindow):
    def __init__(self,dirin,era):
        super().__init__()
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
        self.dailyAnomaly_yes .setChecked(True)
        self.dailyAnomaly_yes.toggled.connect(self.ondailyAnomalyClicked)
        vbox.addWidget(self.dailyAnomaly_yes)
        self.dailyAnomaly_no = QRadioButton("No")
        vbox.addWidget(self.dailyAnomaly_no)

        self.rmm = True
        #RMM Index
        rmm_label = QLabel('Compute RMM Index:', self)
        groupbox = QGroupBox()
        vbox = QVBoxLayout()
        groupbox.setLayout(vbox)
        self.rmm_yes = QRadioButton("Yes")
        self.rmm_yes .setChecked(False)
        self.rmm_yes.toggled.connect(self.onrmmClicked)
        vbox.addWidget(self.rmm_yes)
        self.rmm_no = QRadioButton("No")
        vbox.addWidget(self.rmm_no)
        

        
        
        self.dirin=dirin
        but = QPushButton('Next', self)
        but.clicked.connect(self.openThirdWindow)

        

        self.dirin = dirin
        prefix = self.dirin+"/OBS/"
        print(prefix)
        #change labels correctly.
        dir_in_label = QLabel('Path to OLR data files:', self)
        self.dir_in_text = QLineEdit(self)
        self.dir_in_text.setText(prefix)
        self.dir_in_text.setCursorPosition(len(prefix))

        zonalpath = QLabel('Path to zonal wind at 850 hPa data files:', self)
        self.zonalpathT  = QLineEdit(self)
        
        self.zonalpathT.setText(prefix)
        self.zonalpathT.setCursorPosition(len(prefix))
        

        zonalpath200 = QLabel('Path to zonal wind at 200 hPa data files:', self)
        self.zonalpath200T = QLineEdit(self)
        self.zonalpath200T.setText(prefix)
        self.zonalpath200T.setCursorPosition(len(prefix))

        but = QPushButton('Submit', self)
        but.clicked.connect(self.openThirdWindow)

        self.groupbox = QGroupBox()
        vbox = QVBoxLayout()
        self.groupbox.setLayout(vbox)
        vbox.addWidget(dir_in_label)
        vbox.addWidget(self.dir_in_text)
        vbox.addWidget(zonalpath)
        vbox.addWidget(self.zonalpathT)
        vbox.addWidget(zonalpath200)
        vbox.addWidget(self.zonalpath200T)
        vbox.addWidget(but)
        
        # Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        left_layout.addWidget(weather_image)
        left_layout.addStretch()

        # Create a layout for the right half (text widgets and button)
        self.right_layout = QVBoxLayout()
        
        self.right_layout.addWidget(dailyAnomaly_label)
        self.right_layout.addWidget(groupbox2)
        self.right_layout.addWidget(rmm_label)
        self.right_layout.addWidget(groupbox)
        self.right_layout.addWidget(but)
        self.right_layout.addStretch()
        

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
        dict_file=[]
        if self.dailyAnomaly:
            dict_file.append({'Daily Anomaly:' : True})
        else:
            dict_file.append({'Daily Anomaly:' : False})
        if self.rmm:
            dict_file.append({'RMM:' : True})
        else:
            dict_file.append({'RMM:' : False})

        yaml.dump(dict_file, file)
        self.third_window = ThirdWindow(self.dirin,self.era)
        self.third_window.showMaximized()
        #self.close()

    def method(self,checked):
        # printing the checked status
        if checked:
            self.right_layout.addWidget(self.groupbox)
            #self.right_layout.addStretch()
            
        else:
            self.groupbox.setParent(None)
            #self.close()

class RMM(QMainWindow):
    def __init__(self,dirin,era):
        super().__init__()
        
        self.setWindowTitle('Daily Anomaly and RMM')
        self.setGeometry(0, 0, 800, 400)  # Set window position and size
        self.showMaximized()
        # Create the weather image widget
        weather_image = QLabel(self)
        pixmap = QPixmap('weather.jpg') 
        self.era=era
        #Replace with the actual path to your weather image file
        #Scale the pixmap to fit the size of the QLabel
        #pixmap = pixmap.scaled(weather_image.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        weather_image.setPixmap(pixmap)
        weather_image.resize(pixmap.width(),pixmap.height())
        # Set the size policy of the QLabel to expand and fill the available space
        weather_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Create the text widgets

        

        # Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        left_layout.addWidget(weather_image)
        left_layout.addStretch()

        # Create a layout for the right half (text widgets and button)
        right_layout = QVBoxLayout()
        right_layout.addWidget(dir_in_label)
        right_layout.addWidget(self.dir_in_text)
        right_layout.addWidget(start_date_label)
        right_layout.addWidget(self.start_date_text)
        right_layout.addWidget(end_date_label)
        right_layout.addWidget(self.end_date_text)
        right_layout.addWidget(but)
        right_layout.addStretch()

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

    def openThirdWindow(self):
        self.fourth_window = ThirdWindow(self.dirin,self.era)
        self.fourth_window.showMaximized()
        #self.close()


class ThirdWindow(QMainWindow):
    def __init__(self,dirin,era):
        super().__init__()
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

        self.ten = QCheckBox("Surface air temperature")
        self.ten.setChecked(False)

        # Create the checkboxs
        but = QPushButton('Submit', self)
        but.clicked.connect(self.openThirdSubWindow)
        
        # Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        left_layout.addWidget(weather_image)
        left_layout.addStretch()

        # Create a layout for the right half (text widgets and button)
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.all)
        right_layout.addWidget(self.first)
        right_layout.addWidget(self.second)
        right_layout.addWidget(self.third)
        right_layout.addWidget(self.fourth)
        right_layout.addWidget(self.fifth)
        right_layout.addWidget(self.sixth)
        right_layout.addWidget(self.seventh)
        right_layout.addWidget(self.eight)
        right_layout.addWidget(self.nine)
        right_layout.addWidget(self.ten)
        
        right_layout.addWidget(but)
        right_layout.addStretch()

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
            if self.ten.isChecked():
                selected.append(10)
        self.ThirdSubWindow = ThirdSubWindow(selected,self.dirin,self.era)
        self.ThirdSubWindow.showMaximized()
        #self.close()

    def method(self,checked):
        # printing the checked status
        if checked:
            self.all.setChecked(True)
            self.first.setChecked(True)
            self.second.setChecked(True)
            self.third.setChecked(True)
            self.fourth.setChecked(True)
            self.fifth.setChecked(True)
            self.sixth.setChecked(True)
            self.seventh.setChecked(True)
            self.eight.setChecked(True)
            self.nine.setChecked(True)
            self.ten.setChecked(True)
        else:
            self.all.setChecked(False)
            self.first.setChecked(False)
            self.second.setChecked(False)
            self.third.setChecked(False)
            self.fourth.setChecked(False)
            self.fifth.setChecked(False)
            self.sixth.setChecked(False)
            self.seventh.setChecked(False)
            self.eight.setChecked(False)
            self.nine.setChecked(False)
            self.ten.setChecked(False)

 
        


class ThirdSubWindow(QMainWindow):
    def __init__(self,selected,dirin,era):
        super().__init__()
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
        prefix = self.dirin+"/OBS/"
        print(prefix)
        #change labels correctly.

        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        right_layout = QVBoxLayout(self)
        
        # Path to Z500 data files:
        z500 = QLabel('Path to Z500 model data files:', self)
        self.z500T = QLineEdit(self)
        z500obs = QLabel('Path to Z500 observational data files:', self)
        self.z500Tobs = QLineEdit(self)

        # Path to Z100 data files:
        z100 = QLabel('Path to Z100 model data files:', self)
        self.z100T = QLineEdit(self)
        z100obs = QLabel('Path to Z100 observational data files:', self)
        self.z100Tobs = QLineEdit(self)

        # Path to zonal wind at 850 hPa data files:
        zonalwind850 = QLabel('Path to zonal wind at 850 hPa model data files:', self)
        self.zonalwind850T = QLineEdit(self)
        zonalwind850obs = QLabel('Path to zonal wind at 850 hPa observational data files:', self)
        self.zonalwind850Tobs = QLineEdit(self)

        # Path to zonal wind at 10 hPa data files:
        zonalwind10 = QLabel('Path to zonal wind at 10 hPa model data files:', self)
        self.zonalwind10T = QLineEdit(self)
        zonalwind10obs = QLabel('Path to zonal wind at 10 hPa observational data files:', self)
        self.zonalwind10Tobs = QLineEdit(self)

        # Path to meridional wind at 850 hPa data files:
        meridionalwind850 = QLabel('Path to meridional wind at 850 hPa model data files:', self)
        self.meridionalwind850T = QLineEdit(self)
        meridionalwind850obs = QLabel('Path to meridional wind at 850 hPa data files:', self)
        self.meridionalwind850Tobs = QLineEdit(self)

        # Path to meridional wind at 500 hPa data files:
        meridionalwind500 = QLabel('Path to meridional wind at 500 hPa model data files:', self)
        self.meridionalwind500T = QLineEdit(self)
        meridionalwind500obs = QLabel('Path to meridional wind at 500 hPa data files:', self)
        self.meridionalwind500Tobs = QLineEdit(self)

         # Path to temperature at 500 hPa data files:
        temperature500 = QLabel('Path to temperature at 500 hPa model data files:', self)
        self.temperature500T = QLineEdit(self)
        temperature500obs = QLabel('Path to temperature at 500 hPa data files:', self)
        self.temperature500Tobs = QLineEdit(self)

        # Path to T2m data files:
        t2m = QLabel('Path to T2m model data files:', self)
        self.t2mT = QLineEdit(self)
        t2mobs = QLabel('Path to T2m observational data files:', self)
        self.t2mTobs = QLineEdit(self)

        # Path to precipitational data files:
        precData = QLabel('Path to precipitation model data files:', self)
        self.precDataT = QLineEdit(self)
        precDataobs = QLabel('Path to precipitation observational data files:', self)
        self.precDataTobs = QLineEdit(self)

        weeks = QLabel('Select weeks:', self)
        self.selectweeks = QLineEdit(self)

        #Compute the of Z500 anomalies
        self.z500anomalies = QCheckBox("Copmute the z500 anomalies")
        self.z500anomalies.setChecked(False)

        self.dailyMean= QCheckBox("Model input file daily mean?")
        self.dailyMean.setChecked(False)

        but = QPushButton('Submit', self)
        but.clicked.connect(self.submi)

###########
        
        
        
        rendered=[]
        if(len(selected)>=1):
            if (selected[0]==0):
                rendered.append('z500T')
                right_layout.addWidget(z500)
                right_layout.addWidget(self.z500T)
                if era == False:
                    right_layout.addWidget(z500obs)
                    right_layout.addWidget(self.z500Tobs)
                rendered.append('z100T')
                right_layout.addWidget(z100)
                right_layout.addWidget(self.z100T)
                if era == False:
                    right_layout.addWidget(z100obs)
                    right_layout.addWidget(self.z100Tobs)

                rendered.append('zonalwind850T')
                right_layout.addWidget(zonalwind850)
                right_layout.addWidget(self.zonalwind850T)
                if era == False:
                    right_layout.addWidget(zonalwind850obs)
                    right_layout.addWidget(self.zonalwind850Tobs)

                rendered.append('meridionalwind850T')
                right_layout.addWidget(meridionalwind850)
                right_layout.addWidget(self.meridionalwind850T)
                if era == False:
                    right_layout.addWidget(meridionalwind850obs)
                    right_layout.addWidget(self.meridionalwind850Tobs)

                rendered.append('meridionalwind500T')
                right_layout.addWidget(meridionalwind500)
                right_layout.addWidget(self.meridionalwind500T)
                if era == False:
                    right_layout.addWidget(meridionalwind500obs)
                    right_layout.addWidget(self.meridionalwind500Tobs)

                rendered.append('zonalwind10T')
                right_layout.addWidget(zonalwind10)
                right_layout.addWidget(self.zonalwind10T)
                if era == False:
                    right_layout.addWidget(zonalwind10obs)
                    right_layout.addWidget(self.zonalwind10Tobs)

                rendered.append('temperature500T')
                right_layout.addWidget(temperature500)
                right_layout.addWidget(self.temperature500T)
                if era == False:
                    right_layout.addWidget(temperature500obs)
                    right_layout.addWidget(self.temperature500Tobs)


                rendered.append('t2mT')
                right_layout.addWidget(t2m)
                right_layout.addWidget(self.t2mT)
                if era == False:
                    right_layout.addWidget(t2mobs)
                    right_layout.addWidget(self.t2mTobs)

                rendered.append('precDataT')
                right_layout.addWidget(precData)
                right_layout.addWidget(self.precDataT)
                if era == False:
                    right_layout.addWidget(precDataobs)
                    right_layout.addWidget(self.precDataTobs)

            else:
                if 1 in selected:
                    if 'z500T' not in rendered:
                        rendered.append('z500T')
                        right_layout.addWidget(z500)
                        right_layout.addWidget(self.z500T)
                        if era == False:
                            right_layout.addWidget(z500obs)
                            right_layout.addWidget(self.z500Tobs)
            
                if 2 in selected:
                    if 'precDataT' not in rendered:
                        rendered.append('precDataT')
                        right_layout.addWidget(precData)
                        right_layout.addWidget(self.precDataT)
                        if era == False:
                            right_layout.addWidget(precDataobs)
                            right_layout.addWidget(self.precDataTobs)

                if 3 in selected: #Fraction of the observed STRIPE
                    if 'z500T' not in rendered:
                        rendered.append('z500T')
                        right_layout.addWidget(z500)
                        right_layout.addWidget(self.z500T)
                        if era == False:
                            right_layout.addWidget(z500obs)
                            right_layout.addWidget(self.z500Tobs)
                    right_layout.addWidget(weeks)
                    right_layout.addWidget(self.selectweeks)
            

                    
                if 4 in selected: #Pattern CC over
                    if 'z500T' not in rendered:
                        rendered.append('z500T')
                        right_layout.addWidget(z500)
                        right_layout.addWidget(self.z500T)
                        if era == False:
                            right_layout.addWidget(z500obs)
                            right_layout.addWidget(self.z500Tobs)
                    right_layout.addWidget(self.z500anomalies)
                    
            
                
                if 5 in selected: #relative amplitude over PNA
                    if 'z500T' not in rendered:
                        rendered.append('z500T')
                        right_layout.addWidget(z500)
                        right_layout.addWidget(self.z500T)
                        if era == False:
                            right_layout.addWidget(z500obs)
                            right_layout.addWidget(self.z500Tobs)
                    
                if 6 in selected:
                    if 'z500T' not in rendered:
                        rendered.append('z500T')
                        right_layout.addWidget(z500)
                        right_layout.addWidget(self.z500T)
                        if era == False:
                            right_layout.addWidget(z500obs)
                            right_layout.addWidget(self.z500Tobs)
                    if 'z100T' not in rendered:
                        rendered.append('z100T')
                        right_layout.addWidget(z100)
                        right_layout.addWidget(self.z100T)
                        if era == False:
                            right_layout.addWidget(z100obs)
                            right_layout.addWidget(self.z100Tobs)
                    if 'meridionalwind500T' not in rendered:
                        rendered.append('meridionalwind500T')
                        right_layout.addWidget(meridionalwind500)
                        right_layout.addWidget(self.meridionalwind500T)
                        if era == False:
                            right_layout.addWidget(meridionalwind500obs)
                            right_layout.addWidget(self.meridionalwind500Tobs)
                    
                    if 'temperature500T' not in rendered:
                        rendered.append('temperature500T')
                        right_layout.addWidget(temperature500)
                        right_layout.addWidget(self.temperature500T)
                        if era == False:
                            right_layout.addWidget(temperature500obs)
                            right_layout.addWidget(self.temperature500Tobs)
                    
                    if 'zonalwind10T' not in rendered:
                        rendered.append('zonalwind10T')
                        right_layout.addWidget(zonalwind10)
                        right_layout.addWidget(self.zonalwind10T)
                        if era == False:
                            right_layout.addWidget(zonalwind10obs)
                            right_layout.addWidget(self.zonalwind10Tobs)




                    

                if 7 in selected: #histogram of 10hpa zonal wind
                    if 'zonalwind10T' not in rendered:
                        rendered.append('zonalwind10T')
                        right_layout.addWidget(zonalwind10)
                        right_layout.addWidget(self.zonalwind10T)
                        if era == False:
                            right_layout.addWidget(zonalwind10obs)
                            right_layout.addWidget(self.zonalwind10Tobs)
                    

                if 8 in selected: #Extratropical cyclone activity
                    rendered.append('dailyMean')
                    right_layout.addWidget(self.dailyMean)
                    if 'zonalwind850T' not in rendered:
                        rendered.append('zonalwind850T')
                        right_layout.addWidget(zonalwind850)
                        right_layout.addWidget(self.zonalwind850T)
                        if era == False:
                            right_layout.addWidget(zonalwind850obs)
                            right_layout.addWidget(self.zonalwind850Tobs)
                    
                    if 'meridionalwind850T' not in rendered:
                        rendered.append('meridionalwind850T')
                        right_layout.addWidget(meridionalwind850)
                        right_layout.addWidget(self.meridionalwind850T)
                        if era == False:
                            right_layout.addWidget(meridionalwind850obs)
                            right_layout.addWidget(self.meridionalwind850Tobs)
                    
                    if 'z500T' not in rendered:
                        rendered.append('z500T')
                        right_layout.addWidget(z500)
                        right_layout.addWidget(self.z500T)
                        if era == False:
                            right_layout.addWidget(z500obs)
                            right_layout.addWidget(self.z500Tobs)
                    


                    
                if 9 in selected: #Surface air temperature
                    if 'dailyMean' not in rendered:
                        rendered.append('dailyMean')
                        right_layout.addWidget(self.dailyMean)
                    if 'zonalwind850T' not in rendered:
                        rendered.append('zonalwind850T')
                        right_layout.addWidget(zonalwind850)
                        right_layout.addWidget(self.zonalwind850T)
                        if era == False:
                            right_layout.addWidget(zonalwind850obs)
                            right_layout.addWidget(self.zonalwind850Tobs)
                    if 'meridionalwind850T' not in rendered:
                        rendered.append('meridionalwind850T')
                        right_layout.addWidget(meridionalwind850)
                        right_layout.addWidget(self.meridionalwind850T)
                        if era == False:
                            right_layout.addWidget(meridionalwind850obs)
                            right_layout.addWidget(self.meridionalwind850Tobs)
                
                if 10 in selected:
                    rendered.append('t2mT')
                    right_layout.addWidget(t2m)
                    right_layout.addWidget(self.t2mT)
                    if era == False:
                        right_layout.addWidget(t2mobs)
                        right_layout.addWidget(self.t2mTobs)

                    
                        

                    
                    


        right_layout.addWidget(but)    
        right_layout.addStretch()
        
        self.widget.setLayout(right_layout)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)


        # Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        left_layout.addWidget(weather_image)
        left_layout.addStretch()

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
    def submi(self):
        dict_file =[]
        dict_file.append({'z500' : self.z500T.text()})
        dict_file.append({'z500 observational files' : self.z500Tobs.text()})
        dict_file.append({'z100' : self.z100T.text()})
        dict_file.append({'z100 observational files' : self.z100Tobs.text()})
        dict_file.append({'zonalwind850' : self.zonalwind850T.text()})
        dict_file.append({'zonalwind850 observational files' : self.zonalwind850Tobs.text()})
        dict_file.append({'meridional wind at 850 hPa data file' : self.meridionalwind850T.text()})
        dict_file.append({'meridional wind at 850 hPa observational data file' : self.meridionalwind850Tobs.text()})
        dict_file.append({'Path to meridional wind at 500 hPa data files:' : self.meridionalwind500T.text()})
        dict_file.append({'Path to meridional wind at 500 hPa data files:' : self.meridionalwind500Tobs.text()})
        dict_file.append({'zonal wind at 10 hPa data files:' : self.zonalwind10T.text()})
        dict_file.append({'zonal wind at 10 hPa data files:' : self.zonalwind10Tobs.text()})
        dict_file.append({'temperature at 500 hPa data files' : self.temperature500T.text()})
        dict_file.append({'temperature at 500 hPa data files' : self.temperature500Tobs.text()})
        dict_file.append({'Path to precipitation data files:' : self.precDataT.text()})
        dict_file.append({'Path to precipitation data files:' : self.precDataTobs.text()})
        
        yaml.dump(dict_file, file)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    file = open(r'config.yml', 'w') 
    
    entry_window = EntryWindow()
    entry_window.show()
    sys.exit(app.exec())

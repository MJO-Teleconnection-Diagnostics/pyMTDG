from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QDialog, QSplitter, QSizePolicy
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QPixmap
import yaml
from PyQt5.QtCore import QObject, QThread, QRunnable,QThreadPool
import os
import time, sys
import subprocess
import shutil
class FirstWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setupUi(self)
        self.setWindowTitle('MJO Teleconnections Diagnostics')
        self.setGeometry(200, 200, 800, 400)  # Set window position and size
        self.show()

        #Create the weather image widget
        weather_image = QLabel(self)
        pixmap = QPixmap('logo1.jpg') 

        weather_image.setPixmap(pixmap)
        weather_image.resize(pixmap.width(),pixmap.height())
        # Set the size policy of the QLabel to expand and fill the available space
        weather_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Create the text widgets
        weather_image.setAlignment(Qt.AlignCenter)
        welcome_label = QLabel('Welcome to MJO Teleconnections Diagnostics', self)
        welcome_label.setAlignment(Qt.AlignCenter)
        
        button2 = QPushButton('Start', self)
        button2.setFixedSize(70,30)
        #button2.setGeometry(200, 150, 40, 40)
        button2.clicked.connect(self.open_second_window)
        
       
        
        #Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(welcome_label)
        left_layout.addStretch()
        left_layout.addWidget(weather_image)
        
        widgetB = QWidget()
        left_layout.addStretch()
        
        left_layout.addWidget(button2,alignment=Qt.AlignCenter)
        left_layout.addStretch()
        central_widget = QWidget()
        central_widget.setLayout(left_layout)
        self.setCentralWidget(central_widget)

    def open_second_window(self):
        self.second_window = ViewRes_RunCal(self)
        self.hide()
    
diagnostics={'stripesgeopot':1,'stripesprecip':2,'stripesfraction':4,'patterncc_pna':3,'mjo':12,
            'eke':9,'et_cyclone':8,'patterncc_atlantic':11,'t2m':10,'strat_path':6,'pna_relamp':5,'zonal_wind_hist':7}
def get_model_diagnostics(model_name):
    diags=[]
    flag=0
    selected=[]
    for model in models:
        name,diag=model.split()
        if name == model_name:
            diags.append(diag)
            selected.append(diagnostics[diag])
            flag=1
    if flag==0:
        return False,False
        
    return model_name,selected
            
        
class ViewRes_RunCal(QMainWindow):
    def __init__(self,parent):
        super().__init__()
        #self.setupUi(self)
        self.dict_file={}
        self.parent = parent
        self.setWindowTitle('MJO Teleconnections Diagnostics')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        self.show()
        
        ViewRes= QPushButton('View results from previous calculations', self)
        ViewRes.setFixedSize(300,30)
        #button2.setGeometry(200, 150, 40, 40)
        ViewRes.clicked.connect(self.showInputDialog)

        runDiag = QPushButton('Run diagnostics first', self)
        runDiag.setFixedSize(300,30)
        #button2.setGeometry(200, 150, 40, 40)
        runDiag.clicked.connect(self.openrunDiag)
       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(ViewRes,alignment=Qt.AlignCenter)
        layout.addStretch()
        
        
        ryt_layout.addWidget(runDiag,alignment=Qt.AlignCenter)
        ryt_layout.addStretch()
        
        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()


    def openrunDiag(self):
        self.runDiagnostics = EntryWindow(self,self.dict_file)
        self.runDiagnostics.showMaximized()
        self.hide()
    def showInputDialog(self):
        f=0
        while True:
            dialog = InputDialog()
            result = dialog.exec_()
            if result == QDialog.Accepted:
                self.model_name = dialog.input_text.text().lower()
                self.model_name,self.selected = get_model_diagnostics(self.model_name)
                if self.model_name:
                    self.dict_file['model name'] = self.model_name
                    print(f"Accepted: {self.model_name}")
                    f=1
                    break  # Break the loop when valid input is provided
                else:
                    print(self.model_name)
                    self.showErrorMessage("There is no model with this name.")
            else:
                print("Canceled")
                break  # Break the loop if the user cancels the input dialog
        if f==1:
            self.runFinal = FinalWindow(self,self.selected,self.dict_file)
            self.runFinal.showMaximized()
            self.close()
    def showErrorMessage(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.exec_()
    

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.input_label = QLabel('Enter the model name:')
        self.input_text = QLineEdit()
        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_text)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

class EntryWindow(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.dict_file=dict_file
        self.scroll = QScrollArea()
        self.parent=parent
        self.setWindowTitle('MJO Teleconnections Diagnostics')
        self.setGeometry(0, 0, 800, 400)  
        self.showMaximized()

        #dir_in_ilabel = QLabel('DIR_IN: Please enter the input data directory path\nuyuiy',self)
        #start_date_ilabel = QLabel('START_DATE: Please enter the start date',self)
        #end_date_ilabel = QLabel('END_DATE: Please enter the end date',self)
        #legthFor_ilabel = QLabel('Length of the forecats (in days): Please enter the length of the forecats in days',self)
        #num_ensm_ilabel = QLabel('Number of ensembles: Please enter the number of ensembles',self)
        #num_ini_ilabel = QLabel('Number of initial dates: Please enter the number of initial dates',self)
        #ini_dates_ilabel = QLabel('Initial dates: Please enter all the intial dates',self)
        #era_ilabel = QLabel('Use ERA_I for validation: Please check this box if ERA_I is used for validation',self)
        #imerg_ilabel = QLabel('Use IMERG for validation: Please check this box if IMERG is used for validation',self)

        help_label = QLabel('''
                                DIR_IN: Please enter the input data directory path
                                START_DATE: Please enter the start date
                                END_DATE: Please enter the end date
                                Length of the forecats (in days): Please enter the length of the forecats in days
                                Number of ensembles: Please enter the number of ensembles
                                Number of initial dates: Please enter the number of initial dates
                                Initial dates: Please enter all the intial dates
                                Use ERA_I for validation: Please check this box if ERA_I is used for validation
                                Use IMERG for validation: Please check this box if IMERG is used for validation
                            ''')

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
        #left_layout.addWidget(help)
        left_layout.addWidget(help_label)
        left_layout.addStretch()
        
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
        

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(QWidget(objectName='left'))
        splitter.addWidget(QWidget(objectName='right'))
        splitter.setSizes([1, 1])

        # Set the left layout to the first widget of the splitter
        splitter.widget(0).setLayout(left_layout)
        splitter.widget(0).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the right layout to the second widget of the splitter
        splitter.widget(1).setLayout(right_layout)
        splitter.widget(1).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(splitter)
        

        # Create a central widget to hold the splitter
        central_widget = QWidget()
        central_layout = QGridLayout()
        central_layout.addWidget(self.scroll,0,0,1,13)
        
        central_layout.addWidget(back,1,0,alignment=Qt.AlignLeft)
        central_layout.addWidget(button2,1,12,alignment=Qt.AlignRight)
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

        dict_file=self.dict_file
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
        self.second_window = modelInformation(self,self.dir_in_text.text(),self.era,dict_file)
        self.second_window.showMaximized()
        self.hide()

    def closee(self):
        self.close()
        self.parent.show()

class modelInformation(QMainWindow):
    def __init__(self,parent,dir_in_text,era,dict_file):
        super().__init__()
        #self.setupUi(self)
        scroll_bar= QScrollBar(self)
        self.scroll = QScrollArea()
        self.parent=parent
        self.dir_in_text = dir_in_text
        self.era = era
        self.dict_file = dict_file
        self.setWindowTitle("Model's  Information")
        self.setGeometry(0, 0, 800, 400)  
        self.showMaximized()

        help_label = QLabel('''
        DIR_IN: Please enter the input data directory path
        START_DATE: Please enter the start date
        END_DATE: Please enter the end date
        Length of the forecats (in days): Please enter the length of the forecats in days
        Number of ensembles: Please enter the number of ensembles
        Number of initial dates: Please enter the number of initial dates
        Initial dates: Please enter all the intial dates
        Use ERA_I for validation: Please check this box if ERA_I is used for validation
        Use IMERG for validation: Please check this box if IMERG is used for validation
                            ''')
        #Model name
        model_label = QLabel('Model name:', self)
        self.model_name = QLineEdit(self)

        #Are the model data daily-mean values? (Otherwise the data are instantaneous values)
        daily_mean_values_label = QLabel('Are the model data daily-mean values?', self)
        groupbox = QGroupBox()
        vbox = QVBoxLayout()
        groupbox.setLayout(vbox)
        self.daily_mean_values_yes = QRadioButton("Yes")
        self.daily_mean_values_yes.setChecked(True)
        vbox.addWidget(self.daily_mean_values_yes )
        self.daily_mean_values_no = QRadioButton("No")
        self.daily_mean_values_no.toggled.connect(self.clickedNo)
        vbox.addWidget(self.daily_mean_values_no)

        #If "No" in 1, what is the forecast time step interval in the model data?
        self.time_step_interval = QLabel('What is the forecast time step interval in the model data?', self)
        self.groupbox1 = QGroupBox()
        vbox = QVBoxLayout()
        self.groupbox1.setLayout(vbox)
        self.time_step_interval_6 = QRadioButton("6")
        
        vbox.addWidget(self.time_step_interval_6)
        self.time_step_interval_24 = QRadioButton("24")
        self.time_step_interval_24.setChecked(True)
        vbox.addWidget(self.time_step_interval_24)

        #Does the model data include the initial conditions?
        self.initial_conds_label = QLabel('Does the model data include the initial conditions?', self)
        self.groupbox2 = QGroupBox()
        vbox = QVBoxLayout()
        self.groupbox2.setLayout(vbox)
        self.initial_conds_yes = QRadioButton("Yes")
        self.initial_conds_yes.setChecked(True)
        vbox.addWidget(self.initial_conds_yes)
        self.initial_conds_no = QRadioButton("No")
        vbox.addWidget(self.initial_conds_no)

        #Smooth climatology
        self.smooth_climatology_label = QLabel('Smooth climatology?', self)
        self.groupbox3 = QGroupBox()
        vbox = QVBoxLayout()
        self.groupbox3.setLayout(vbox)
        self.smooth_climatology_yes = QRadioButton("Yes")
        self.smooth_climatology_yes.setChecked(True)
        vbox.addWidget(self.smooth_climatology_yes)
        self.smooth_climatology_no = QRadioButton("No")
        vbox.addWidget(self.smooth_climatology_no)

        self.button2 = QPushButton('Next', self)
        self.button2.setFixedSize(70,30)
        self.button2.clicked.connect(self.open_second_window)
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)

        #Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
            
        left_layout.addStretch()
    
        left_layout.addWidget(help_label)
        left_layout.addStretch()
        left_layout.addWidget(back,alignment=Qt.AlignLeft)
        self.left_layout = left_layout
        

        #Create a layout for the right half (text widgets and button)
        right_layout = QVBoxLayout()
        right_layout.addStretch()
        right_layout.addWidget(model_label)
        right_layout.addWidget(self.model_name)
        right_layout.addWidget(daily_mean_values_label)
        right_layout.addWidget(groupbox)
        
        right_layout.addWidget(self.initial_conds_label)
        right_layout.addWidget(self.groupbox2)
        right_layout.addWidget(self.smooth_climatology_label)
        right_layout.addWidget(self.groupbox3)
        right_layout.addStretch()
        right_layout.addWidget(self.button2,alignment=Qt.AlignRight)
        
        self.right_layout = right_layout
        # Create a QSplitter to split the window equally
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(QWidget(objectName = "left"))
        splitter.addWidget(QWidget(objectName = "right"))
        splitter.setSizes([1, 1])

        # Set the left layout to the first widget of the splitter
        splitter.widget(0).setLayout(left_layout)
        splitter.widget(0).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the right layout to the second widget of the splitter
        splitter.widget(1).setLayout(right_layout)
        splitter.widget(1).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        splitter.widget(0).setStyleSheet("QWidget#left { border-width: 3px; border-style: solid; border-color: black white black black; }")
        splitter.widget(1).setStyleSheet("QWidget#right { border-width: 3px; border-style: solid; border-color: black white black black ; }")

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(splitter)
        

        # Create a central widget to hold the splitter
        central_widget = QWidget()
        central_layout = QGridLayout()
        central_layout.addWidget(self.scroll,0,0,1,13)
        
        central_layout.addWidget(back,1,0,alignment=Qt.AlignLeft)
        central_layout.addWidget(self.button2,1,12,alignment=Qt.AlignRight)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def clickedNo(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            if not self.time_step_interval or not self.groupbox1:
                self.time_step_interval = QLabel('What is the forecast time step interval in the model data?', self)
                self.groupbox1 = QGroupBox()
                vbox = QVBoxLayout()
                self.groupbox1.setLayout(vbox)
                self.time_step_interval_6 = QRadioButton("6")
                
                vbox.addWidget(self.time_step_interval_6)
                self.time_step_interval_24 = QRadioButton("24")
                self.time_step_interval_24.setChecked(True)
                vbox.addWidget(self.time_step_interval_24)
            self.right_layout.insertWidget(5,self.time_step_interval)
            self.right_layout.insertWidget(6,self.groupbox1)
        else:
            self.right_layout.removeWidget(self.time_step_interval)
            self.time_step_interval.deleteLater()
            self.time_step_interval = None
            self.right_layout.removeWidget(self.groupbox1)
            self.groupbox1.deleteLater()
            self.groupbox1 = None
        
        



    def open_second_window(self):
        #commenting out the input validation
        dict_file =self.dict_file
        dict_file['model name'] = self.model_name.text()
        #dict_file['model data daily-mean values'] = self.daily_mean_values_yes.isChecked()
        if self.time_step_interval and self.time_step_interval_24.isChecked():
            dict_file['forecast time step']= 24
        else:
            dict_file['forecast time step']= 6
        
        dict_file['model initial conditions']= self.initial_conds_yes.isChecked()
        dict_file['smooth climatology:'] = self.smooth_climatology_yes.isChecked()
        
        self.dict_file = dict_file
        
        self.second_window = SecondWindow(self,self.dir_in_text,self.era,dict_file)
        self.second_window.showMaximized()
        self.hide()
    

    
    def closee(self):
        self.close()
        self.parent.show()




class SecondWindow(QMainWindow):
    def __init__(self,parent,dirin,era,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.scroll = QScrollArea()
        self.parent=parent
        self.dict_file = dict_file
        self.setWindowTitle('Daily Anomaly and RMM')
        self.setGeometry(0, 0, 800, 400)  # Set window position and size
        self.showMaximized()
        #Create the weather image widget
        weather_image = QLabel(self)
        pixmap = QPixmap('weather.jpg') 
        self.era = era

        help_label = QLabel('''
        DIR_IN: Please enter the input data directory path
        START_DATE: Please enter the start date
        END_DATE: Please enter the end date
        Length of the forecats (in days): Please enter the length of the forecats in days
        Number of ensembles: Please enter the number of ensembles
        Number of initial dates: Please enter the number of initial dates
        Initial dates: Please enter all the intial dates
        Use ERA_I for validation: Please check this box if ERA_I is used for validation
        Use IMERG for validation: Please check this box if IMERG is used for validation
                            ''')
       
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

        but = QPushButton('Next', self)
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
        left_layout.addWidget(help_label)
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
        splitter.addWidget(QWidget(objectName = 'left'))
        splitter.addWidget(QWidget(objectName = 'right'))
        splitter.setSizes([1, 1])

        # Set the left layout to the first widget of the splitter
        splitter.widget(0).setLayout(left_layout)
        splitter.widget(0).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the right layout to the second widget of the splitter
        splitter.widget(1).setLayout(self.right_layout)
        splitter.widget(1).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(splitter)
        

        # Create a central widget to hold the splitter
        central_widget = QWidget()
        central_layout = QGridLayout()
        central_layout.addWidget(self.scroll,0,0,1,13)
        
        central_layout.addWidget(back,1,0,alignment=Qt.AlignLeft)
        central_layout.addWidget(but,1,12,alignment=Qt.AlignRight)
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
            self.right_layout.insertWidget(4,self.groupbox)
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
        self.setWindowTitle('Select which diagnostic you want to run')
        self.setGeometry(0, 0, 800, 400)  # Set window position and size
        self.showMaximized()
        # Create the weather image widget
        #weather_image = QLabel(self)
        #pixmap = QPixmap('weather.jpg') 

        help_label = QLabel('''
        DIR_IN: Please enter the input data directory path
        START_DATE: Please enter the start date
        END_DATE: Please enter the end date
        Length of the forecats (in days): Please enter the length of the forecats in days
        Number of ensembles: Please enter the number of ensembles
        Number of initial dates: Please enter the number of initial dates
        Initial dates: Please enter all the intial dates
        Use ERA_I for validation: Please check this box if ERA_I is used for validation
        Use IMERG for validation: Please check this box if IMERG is used for validation
                            ''')
        
        self.scroll = QScrollArea()
        #Replace with the actual path to your weather image file
        #Scale the pixmap to fit the size of the QLabel
        #pixmap = pixmap.scaled(weather_image.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        '''weather_image.setPixmap(pixmap)
        weather_image.resize(pixmap.width(),pixmap.height())
        # Set the size policy of the QLabel to expand and fill the available space
        weather_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)'''
        # Create the text widgets
        
        self.dirin = dirin
        self.era=era
        self.all = QCheckBox("Select All")
        self.all.setChecked(False)
        self.all.stateChanged.connect(self.method)

        self.first = QCheckBox("STRIPES Index for geopotential height")
        self.first.setChecked(False)

        self.second = QCheckBox("STRIPES Index for precipitation")
        self.second.setChecked(False)

        self.third = QCheckBox("Pattern CC over the PNA region")
        self.third.setChecked(False)

        self.third_2 = QCheckBox("Pattern CC over the Euro-Atlantic sector")
        self.third_2.setChecked(False) #11

        self.fourth = QCheckBox("Fraction of the observed STRIPES index for geopotential height")
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
        but = QPushButton('Next', self)
        but.setFixedSize(70,30)
        but.clicked.connect(self.openThirdSubWindow)
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        
        # Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        left_layout.addWidget(help_label)
        left_layout.addStretch()
        
        

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

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(QWidget(objectName = 'left'))
        splitter.addWidget(QWidget(objectName = 'right'))
        splitter.setSizes([1, 1])

        # Set the left layout to the first widget of the splitter
        splitter.widget(0).setLayout(left_layout)
        splitter.widget(0).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        splitter.widget(1).setLayout(right_layout)
        splitter.widget(1).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(splitter)
        

        # Create a central widget to hold the scroll
        central_widget = QWidget()
        central_layout = QGridLayout()
        central_layout.addWidget(self.scroll,0,0,1,13)
        
        central_layout.addWidget(back,1,0,alignment=Qt.AlignLeft)
        central_layout.addWidget(but,1,12,alignment=Qt.AlignRight)
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
        self.dict_file['selected']=selected
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
        #vbox = QHBoxLayout()
        self.setWindowTitle('Third Sub Window')
        self.setGeometry(0, 0, 800, 400)  # Set window position and size
        self.showMaximized()
        scroll_bar = QScrollBar(self)
        # Create the weather image widget
        #weather_image = QLabel(self)
        #pixmap = QPixmap('weather.jpg') 
        self.threadpool = QThreadPool()
        help_label = QLabel('''
        DIR_IN: Please enter the input data directory path
        START_DATE: Please enter the start date
        END_DATE: Please enter the end date
        Length of the forecats (in days): Please enter the length of the forecats in days
        Number of ensembles: Please enter the number of ensembles
        Number of initial dates: Please enter the number of initial dates
        Initial dates: Please enter all the intial dates
        Use ERA_I for validation: Please check this box if ERA_I is used for validation
        Use IMERG for validation: Please check this box if IMERG is used for validation
                            ''')
        
        #Replace with the actual path to your weather image file
        #Scale the pixmap to fit the size of the QLabel
        #pixmap = pixmap.scaled(weather_image.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        '''weather_image.setPixmap(pixmap)
        weather_image.resize(pixmap.width(),pixmap.height())
        # Set the size policy of the QLabel to expand and fill the available space
        weather_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)'''
        # Create the text widgets
        
        self.dirin = dirin
        pref = self.dirin+"/"
        prefix = self.dirin+"/OBS/"
        
        #change labels correctly.

        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        right_layout = QVBoxLayout()

        num_dates = dict_file['Number of initial dates:']
        dates = dict_file['Initial dates:' ]
        

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

        but = QPushButton('Run', self)
        but.setFixedSize(70,30)
        but.clicked.connect(self.submi)
        
        showRes = QPushButton('Show results', self)
        showRes.setFixedSize(100,30)
        showRes.clicked.connect(self.showResults)
        
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

                if 3 in selected or 11 in selected: #Fraction of the observed STRIPES
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
        self.selected=selected       
        right_layout.addStretch()
        #right_layout.addWidget(but,alignment=Qt.AlignRight)    

        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)

        # Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        left_layout.addWidget(help_label)
        left_layout.addStretch()
        #left_layout.addWidget(back,alignment=Qt.AlignLeft)
        # Create a layout for the right half (text widgets and button)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(QWidget(objectName = 'left'))
        splitter.addWidget(QWidget(objectName = 'right'))
        splitter.setSizes([1, 1])

        # Set the left layout to the first widget of the splitter
        splitter.widget(0).setLayout(left_layout)
        splitter.widget(0).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the right layout to the second widget of the splitter
        splitter.widget(1).setLayout(right_layout)
        splitter.widget(1).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(splitter)
        

        # Create a central widget to hold the scroll
        central_widget = QWidget()
        central_layout = QGridLayout()
        central_layout.addWidget(self.scroll,0,0,1,13)
        
        central_layout.addWidget(back,1,0,alignment=Qt.AlignLeft)
        central_layout.addWidget(showRes,1,5,alignment=Qt.AlignCenter)
        central_layout.addWidget(but,1,12,alignment=Qt.AlignRight)
        central_widget.setLayout(central_layout)
        
        self.setCentralWidget(central_widget)
    
    def closee(self):
        self.close()
        self.parent.show()
    def submi(self):
        slurm=self.showInputDialog()
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
        dict_file['selected']=self.selected
        file = open(r'config.yml', 'w') 
        yaml.dump(dict_file, file)
        file.close()
        
        #run diagnostics
        diagnostics_path = ["../T2m_composites/t2m_composites.py", "../T2m_composites/t2m_composites.py", "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py"]
        paths = 'python '+diagnostics_path[self.selected[0]]
        for i in self.selected[1:]:
            paths+=' & python '+diagnostics_path[i]
        
        if slurm:
            command=f"salloc  -p normal  -n 4  --cpus-per-task=12 --mem=8GB -t 0-02:00:00 bash -c 'source ../../miniconda/bin/activate; conda activate mjo_telecon;{paths}'"
            #self.ret = subprocess.Popen(command,  shell=True)
            
        else:
            
            command = paths
            
            #command='cd ..; cd T2m_composites; python t2m_composites.py & python t2m_composites.py & python t2m_composites.py'
            #self.ret = subprocess.Popen(command,  shell=True)
        
        self.hide()
        dialog=LoadingDialog(self,command,self.selected,dict_file)  
        #self.ret.wait()
        dialog.exec_()
        
        
    def showResults(self):
        self.nextwindow=FinalWindow(self,self.selected,self.dict_file)
        self.nextwindow.showMaximized()
        self.hide()
        
    def showInputDialog(self):
        dialog = InputDialog2()
        result = dialog.exec_()
        if result == QDialog.Accepted:
            return True
        else:
            return False  
    
class SubprocessRunner(QThread):
    def __init__(self, command):
        super(SubprocessRunner, self).__init__()
        self.command = command

    def run(self):
        '''self.processes=[]
        for path in self.command:
            try:
                process = subprocess.Popen(['python', path])
                self.processes.append(process)
            except Exception as e:
                print(f"Error running script {path}: {e}")

    # Wait for all subprocesses to complete
        for process in self.processes:
            process.wait()'''
        self.ret = subprocess.Popen(self.command, shell=True)
        self.ret.wait()
        print('Execution done in Subprocess thread')

class InputDialog2(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout=QGridLayout()
        self.input_label = QLabel('Are you using SLURM to run resource-intensive jobs?')
        self.ok_button = QPushButton('Yes')
        self.cancel_button = QPushButton('No')
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.input_label,0,0)
        layout.addWidget(self.ok_button,1,0,alignment=Qt.AlignLeft)
        layout.addWidget(self.cancel_button,1,12,alignment=Qt.AlignRight)
        self.setLayout(layout)
        
class LoadingDialog(QDialog):
    def __init__(self, parent,command,selected,dict_file,):
        #super(LoadingDialog, self).__init__()
        super().__init__()
        self.selected=selected
        self.parent=parent
        self.dict_file=dict_file
        
        self.subprocess_runner = SubprocessRunner(command)
        self.subprocess_runner.finished.connect(self.close)

        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.setLabelText("Running diagnostics...")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setRange(0, 0)  # Set to an indeterminate progress bar
        self.progress_dialog.setWindowTitle("Please wait")
        self.progress_dialog.rejected.connect(self.close)
        self.subprocess_runner.start()
    def on_rejected(self):
        self.subprocess_runner.ret.terminate()
        self.subprocess_runner.ret.wait()
        self.subprocess_runner.terminate()  # Terminate the subprocess
        print('terminated')
        self.subprocess_runner.wait()  # Wait for the subprocess to finish
        self.close()

    def closeEvent(self, event):
        if self.subprocess_runner.isRunning():
            print('terminated')
            self.subprocess_runner.ret.terminate()
            self.subprocess_runner.ret.wait()
            self.close()
            self.parent.show()
            event.accept()
        else:
            print('About to close the loading page')
            self.close()
            self.parent.show()
            event.accept()


def get_all_files_in_directory(directory):
    # Check if the path is a directory
    abs_directory = os.path.abspath(directory)
    
    # Check if the path is a directory
    if not os.path.isdir(abs_directory):
        print(f"{abs_directory} is not a valid directory.")
        return
    
    # Get a list of all files in the directory
    files = [os.path.join(abs_directory, file) for file in os.listdir(abs_directory) if os.path.isfile(os.path.join(abs_directory, file))]
    
    return files

class runCal_View(QMainWindow):
    def __init__(self,parent):
        super().__init__()
        #self.setupUi(self)
        self.dict_file={}
        self.parent = parent
        self.setWindowTitle('')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        self.show()
        
        self.run= QPushButton('Run Calculations', self)
        self.run.setFixedSize(300,30)
        #button2.setGeometry(200, 150, 40, 40)
        self.run.clicked.connect(self.runn)

        self.showw = QPushButton('Show results', self)
        self.showw.setFixedSize(700,30)
        #button2.setGeometry(200, 150, 40, 40)
        self.showw.clicked.connect(self.showResults)
       
        self.back = QPushButton('Back', self)
        self.back.setFixedSize(70,30)
        self.back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.run,alignment=Qt.AlignCenter)
        self.layout.addStretch()
        

        # Create a central widget to hold the splitter
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()


    def showResults(self):
        self.runDiagnostics = EntryWindow(self,self.dict_file)
        self.runDiagnostics.showMaximized()
        self.hide()
    def runn(self):
        f=0
        while True:
            dialog = InputDialog()
            result = dialog.exec_()
            if result == QDialog.Accepted:
                self.model_name = dialog.input_text.text().lower()
                self.model_name,self.selected = get_model_diagnostics(self.model_name)
                if self.model_name:
                    self.dict_file['model name'] = self.model_name
                    print(f"Accepted: {self.model_name}")
                    f=1
                    break  # Break the loop when valid input is provided
                else:
                    print(self.model_name)
                    self.showErrorMessage("There is no model with this name.")
            else:
                print("Canceled")
                break  # Break the loop if the user cancels the input dialog
        if f==1:
            self.runFinal = FinalWindow(self,self.selected,self.dict_file)
            self.runFinal.showMaximized()
            self.close()
    


class FinalWindow(QMainWindow):
    def __init__(self,parent,selected,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.scroll = QScrollArea()  
        self.parent=parent
        self.dict_file=dict_file
        self.selected = selected
        self.setWindowTitle('Select what you want to view')
        self.setGeometry(0, 0, 800, 400)  # Set window position and size
        self.showMaximized()
        # Create the weather image widget
        #weather_image = QLabel(self)
        #pixmap = QPixmap('weather.jpg') 

        help_label = QLabel('''
        DIR_IN: Please enter the input data directory path
        START_DATE: Please enter the start date
        END_DATE: Please enter the end date
        Length of the forecats (in days): Please enter the length of the forecats in days
        Number of ensembles: Please enter the number of ensembles
        Number of initial dates: Please enter the number of initial dates
        Initial dates: Please enter all the intial dates
        Use ERA_I for validation: Please check this box if ERA_I is used for validation
        Use IMERG for validation: Please check this box if IMERG is used for validation
                            ''')
        
        '''weather_image.setPixmap(pixmap)
        weather_image.resize(pixmap.width(),pixmap.height())
        # Set the size policy of the QLabel to expand and fill the available space
        weather_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        '''
        self.first = QRadioButton("STRIPES Index for geopotential height")
        self.first.setChecked(False) # 1

        self.second = QRadioButton("STRIPES Index for precipitation")
        self.second.setChecked(False) #2

        self.third = QRadioButton("Pattern CC over the PNA region")
        self.third.setChecked(False) #3

        self.third_2 = QRadioButton("Pattern CC over the Euro-Atlantic sector")
        self.third_2.setChecked(False) #11

        self.fourth = QRadioButton("Fraction of the observed STRIPES index for geopotential height")
        self.fourth.setChecked(False) #4

        self.fifth = QRadioButton("Relative amplitude over PNA?")
        self.fifth.setChecked(False) #5

        self.sixth = QRadioButton("Stratospheric pathway")
        self.sixth.setChecked(False) #6

        self.seventh = QRadioButton("Histogram of 10 hPa zonal wind")
        self.seventh.setChecked(False) #7

        self.eight = QRadioButton("Extratropical cyclone activity")
        self.eight.setChecked(False) #8

        self.nine = QRadioButton("EKE850-Z500 correlation")
        self.nine.setChecked(False) #9

        self.nine_two = QRadioButton("MJO")
        self.nine_two.setChecked(False) #12

        self.ten = QRadioButton("Surface air temperature")
        self.ten.setChecked(False) #10

        
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)

        next = QPushButton('Next', self)
        next.setFixedSize(70,30)
        next.clicked.connect(self.showResults)
        
        
        
        # Create a layout for the left half (weather image)
        left_layout = QVBoxLayout()
        left_layout.addWidget(help_label)
        left_layout.addStretch()
        left_layout.addWidget(back,alignment=Qt.AlignLeft)
        
        result_label = QLabel('Show results for:')
        # Create a layout for the right half (text widgets and button)
        right_layout = QVBoxLayout()
        right_layout.addWidget(result_label)
        
        
        for i in selected:
            if i == 0:

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
                
            else:
                if i == 1:
                    right_layout.addWidget(self.first)
                    
                if i == 2:
                    right_layout.addWidget(self.second)
                    
                if i==3:
                    right_layout.addWidget(self.third)
                    
                if i ==11:
                    right_layout.addWidget(self.third_2)
                    
                if i==4:
                    right_layout.addWidget(self.fourth)
                    
                if i==5:
                    right_layout.addWidget(self.fifth)
                    
                if i==6:
                    right_layout.addWidget(self.sixth)
                    
                if i==7:
                    right_layout.addWidget(self.seventh)
                    
                if i==8:
                    right_layout.addWidget(self.eight)
                    
                if i==9:
                    right_layout.addWidget(self.nine)
                    
                if i==12:
                    right_layout.addWidget(self.nine_two)
                    
                if i==10:
                    right_layout.addWidget(self.ten)
                    

        right_layout.addStretch() 
        right_layout.addWidget(next,alignment=Qt.AlignRight)
        #right_layout.addWidget(but,alignment=Qt.AlignRight)
        # Create a QSplitter to split the window equally
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(QWidget(objectName = 'left'))
        splitter.addWidget(QWidget(objectName = 'right'))
        splitter.setSizes([1, 1])

        # Set the left layout to the first widget of the splitter
        splitter.widget(0).setLayout(left_layout)
        splitter.widget(0).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the right layout to the second widget of the splitter
        splitter.widget(1).setLayout(right_layout)
        splitter.widget(1).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(splitter)
        

        # Create a central widget to hold the splitter
        central_widget = QWidget()
        central_layout = QGridLayout()
        central_layout.addWidget(self.scroll,0,0,1,13)
        
        central_layout.addWidget(back,1,0,alignment=Qt.AlignLeft)
        central_layout.addWidget(next,1,12,alignment=Qt.AlignRight)
        central_widget.setLayout(central_layout)
        
        self.setCentralWidget(central_widget)

    def showResults(self):
        #self.hide()
        f=0
        if self.first.isChecked():
            #open new window
            f=1
            self.win1 = firstResult(self,self.dict_file)
            self.win1.show()
        elif self.second.isChecked():
            f=1
            self.win2 = secondResult(self,self.dict_file)
            self.win2.show()
        elif self.third.isChecked():
            f=1
            self.win2 = thirdResult(self,self.dict_file)
            self.win2.show()
        elif self.third_2.isChecked():
            f=1
            self.win2 = third2Result(self,self.dict_file)
            self.win2.show()
        elif self.fourth.isChecked():
            f=1
            self.win2 = fourthResult(self,self.dict_file)
            self.win2.show()
        elif self.fifth.isChecked():
            f=1
            self.win2 = fifthResult(self,self.dict_file)
            self.win2.show()
        elif self.sixth.isChecked():
            f=1
            self.win2 = sixthResult(self,self.dict_file)
            self.win2.show()
        elif self.seventh.isChecked():
            f=1
            self.win2 = seventhResult(self,self.dict_file)
            self.win2.show()
        elif self.eight.isChecked():
            f=1
            self.win2 = eightResult(self,self.dict_file)
            self.win2.show()
        elif self.nine.isChecked():
            f=1
            self.win2 = ninthResult(self,self.dict_file)
            self.win2.show()
        elif self.nine_two.isChecked():
            f=1
            self.win2 = nine_twoResult(self,self.dict_file)
            self.win2.show()
        elif self.ten.isChecked():
            f=1
            self.win2 = tenthResult(self,self.dict_file)
            self.win2.show()
        if f==0:
            msg = QMessageBox()
            msg.setWindowTitle("Nothing selected")
            msg.setText("Select at least one to proceed")
            x=msg.exec_()

            return
        else:
            self.hide()

    def closee(self):
        self.close()
        self.parent.show()

class tenthResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.viewImage1 = None
        self.viewImage2 = None
        self.viewImage3 = None
        self.viewImage4 = None
        self.viewImage5 = None
        self.viewImage6 = None
        self.viewImage7= None
        self.viewImage8 = None
        self.model_name = dict_file['model name']
        self.setWindowTitle('Surface air temperature results')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)

        #Create the weather image widget
        self.all_files=get_all_files_in_directory(f'../output/T2m/{self.model_name}')
        
        week1_2 = QPushButton('T2m res - 1', self)
        week1_2.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week1_2.clicked.connect(self.openweek1_2)

        week3_4 = QPushButton('T2m res - 2', self)
        week3_4.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week3_4.clicked.connect(self.openweek3_4)

        
        week5_6 = QPushButton('T2m res - 3', self)
        week5_6.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week5_6.clicked.connect(self.openweek5_6)

        week7_8 = QPushButton('T2m res - 4', self)
        week7_8.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week7_8.clicked.connect(self.openweek7_8)

        week5 = QPushButton('T2m res - 5', self)
        week5.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week5.clicked.connect(self.openweek5)

        week6 = QPushButton('T2m res - 6', self)
        week6.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week6.clicked.connect(self.openweek6)

        week7 = QPushButton('T2m res - 7', self)
        week7.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week7.clicked.connect(self.openweek7)

        week8 = QPushButton('T2m res - 8', self)
        week8.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week8.clicked.connect(self.openweek8)
       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(week1_2,alignment=Qt.AlignCenter)
        layout.addWidget(week3_4,alignment=Qt.AlignCenter)

        layout.addWidget(week5,alignment=Qt.AlignCenter)
        layout.addWidget(week7,alignment=Qt.AlignCenter)
        
        
        ryt_layout.addWidget(week5_6,alignment=Qt.AlignCenter)
        ryt_layout.addWidget(week7_8,alignment=Qt.AlignCenter)

        ryt_layout.addWidget(week6,alignment=Qt.AlignCenter)
        ryt_layout.addWidget(week8,alignment=Qt.AlignCenter)

        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()

    def openweek1_2(self):
        if self.viewImage1 == None or self.viewImage1.isVisible() == False:
            self.viewImage1 = viewImage(self.all_files[0],'T2m - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage1.show()

    def openweek3_4(self):
        if self.viewImage2 == None or self.viewImage2.isVisible() == False:
            self.viewImage2 = viewImage(self.all_files[1],'T2m - 2')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage2.show()
    def openweek5_6(self):
        if self.viewImage3 == None or self.viewImage3.isVisible() == False:
            self.viewImage3 = viewImage(self.all_files[2],'T2m - 3')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage3.show()

    def openweek7_8(self):
        if self.viewImage4 == None or self.viewImage4.isVisible() == False:
            self.viewImage4 = viewImage(self.all_files[3],'T2m - 4')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage4.show()
    def openweek5(self):
        if self.viewImage5 == None or self.viewImage5.isVisible() == False:
            self.viewImage5 = viewImage(self.all_files[4],'T2m - 5')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage5.show()
    def openweek6(self):
        if self.viewImage6 == None or self.viewImage6.isVisible() == False:
            self.viewImage6 = viewImage(self.all_files[5],'T2m - 6')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage6.show()
    def openweek7(self):
        if self.viewImage7 == None or self.viewImage7.isVisible() == False:
            self.viewImage7 = viewImage(self.all_files[6],'T2m - 7')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage7.show()
    def openweek8(self):
        if self.viewImage8 == None or self.viewImage8.isVisible() == False:
            self.viewImage8 = viewImage(self.all_files[7],'T2m - 8')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage8.show()


class nine_twoResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.viewImage1 = None
        self.viewImage2 = None
        self.viewImage3 = None
        self.viewImage4 = None
        self.setWindowTitle('MJO')
        self.model_name = dict_file['model name']
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)

        #Create the weather image widget
        self.all_files=get_all_files_in_directory(f'../output/T2m/{self.model_name}')
        week1_2 = QPushButton('MJO - 1', self)
        week1_2.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week1_2.clicked.connect(self.openweek1_2)

        week3_4 = QPushButton('MJO - 2', self)
        week3_4.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week3_4.clicked.connect(self.openweek3_4)

        
        week5_6 = QPushButton('MJO - 3', self)
        week5_6.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week5_6.clicked.connect(self.openweek5_6)

        

        
       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(week1_2,alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(week3_4,alignment=Qt.AlignCenter)
        
        ryt_layout.addWidget(week5_6,alignment=Qt.AlignCenter)
       
        

        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()

    def openweek1_2(self):
        if self.viewImage1 == None or self.viewImage1.isVisible() == False:
            self.viewImage1 = viewImage(self.all_files[0],'Stripes - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage1.show()

    def openweek3_4(self):
        if self.viewImage2 == None or self.viewImage2.isVisible() == False:
            self.viewImage2 = viewImage(self.all_files[1],'Stripes - 2')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage2.show()
    def openweek5_6(self):
        if self.viewImage3 == None or self.viewImage3.isVisible() == False:
            self.viewImage3 = viewImage(self.all_files[2],'Stripes - 3')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage3.show()
    def openweek7_8(self):
        if self.viewImage4 == None or self.viewImage4.isVisible() == False:
            self.viewImage4 = viewImage(self.all_files[3],'Stripes - 4')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage4.show()




class ninthResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.viewImage1 = None
        self.viewImage2 = None
        self.viewImage3 = None
        self.viewImage4 = None
        self.model_name = dict_file['model name']
        self.setWindowTitle('EKE850-Z500 correlation')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)

        #Create the weather image widget
        
        week1_2 = QPushButton('EKE850-Z500 - 1', self)
        week1_2.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week1_2.clicked.connect(self.openweek1_2)

        week3_4 = QPushButton('EKE850-Z500 - 2', self)
        week3_4.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week3_4.clicked.connect(self.openweek3_4)

        
        week5_6 = QPushButton('EKE850-Z500 - 3', self)
        week5_6.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week5_6.clicked.connect(self.openweek5_6)

        

        
       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(week1_2,alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(week3_4,alignment=Qt.AlignCenter)
        
        ryt_layout.addWidget(week5_6,alignment=Qt.AlignCenter)
       
        

        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()

    def openweek1_2(self):
        if self.viewImage1 == None or self.viewImage1.isVisible() == False:
            self.viewImage1 = viewImage("../output/EKE/"+self.model_name+"/Stripes_1.png",'Stripes - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage1.show()

    def openweek3_4(self):
        if self.viewImage2 == None or self.viewImage2.isVisible() == False:
            self.viewImage2 = viewImage("../output/EKE/"+self.model_name+"/Stripes_2.png",'Stripes - 2')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage2.show()
    def openweek5_6(self):
        if self.viewImage3 == None or self.viewImage3.isVisible() == False:
            self.viewImage3 = viewImage("../output/EKE/"+self.model_name+"/Stripes_3.png",'Stripes - 3')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage3.show()
    def openweek7_8(self):
        if self.viewImage4 == None or self.viewImage4.isVisible() == False:
            self.viewImage4 = viewImage("../output/EKE/"+self.model_name+"/Stripes_4.png",'Stripes - 4')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage4.show()



class eightResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.viewImage1 = None
        self.viewImage2 = None
        self.viewImage3 = None
        self.viewImage4 = None
        self.model_name = dict_file['model name']
        self.setWindowTitle('Extratropical cyclone activity results')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)

        #Create the weather image widget
        
        week1_2 = QPushButton('ET Cyclone res - 1', self)
        week1_2.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week1_2.clicked.connect(self.openweek1_2)

        week3_4 = QPushButton('ET Cyclone res - 2', self)
        week3_4.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week3_4.clicked.connect(self.openweek3_4)

        
        week5_6 = QPushButton('ET Cyclone res - 3', self)
        week5_6.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week5_6.clicked.connect(self.openweek5_6)

        week7_8 = QPushButton('ET Cyclone res - 4', self)
        week7_8.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week7_8.clicked.connect(self.openweek7_8)

        week5 = QPushButton('ET Cyclone res - 5', self)
        week5.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week5.clicked.connect(self.openweek5)

        week6 = QPushButton('ET Cyclone res - 6', self)
        week6.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week6.clicked.connect(self.openweek6)

        week7 = QPushButton('ET Cyclone res - 7', self)
        week7.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week7.clicked.connect(self.openweek7)

        week8 = QPushButton('ET Cyclone res - 8', self)
        week8.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week8.clicked.connect(self.openweek8)
       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(week1_2,alignment=Qt.AlignCenter)
        layout.addWidget(week3_4,alignment=Qt.AlignCenter)

        layout.addWidget(week5,alignment=Qt.AlignCenter)
        layout.addWidget(week7,alignment=Qt.AlignCenter)
        
        
        ryt_layout.addWidget(week5_6,alignment=Qt.AlignCenter)
        ryt_layout.addWidget(week7_8,alignment=Qt.AlignCenter)

        ryt_layout.addWidget(week6,alignment=Qt.AlignCenter)
        ryt_layout.addWidget(week8,alignment=Qt.AlignCenter)

        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()

    def openweek1_2(self):
        if self.viewImage1 == None or self.viewImage1.isVisible() == False:
            self.viewImage1 = viewImage("../output/ET_Cyclone/"+self.model_name+"/Stripes_1.png",'Stripes - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage1.show()

    def openweek3_4(self):
        if self.viewImage2 == None or self.viewImage2.isVisible() == False:
            self.viewImage2 = viewImage("../output/ET_Cyclone/"+self.model_name+"/Stripes_2.png",'Stripes - 2')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage2.show()
    def openweek5_6(self):
        if self.viewImage3 == None or self.viewImage3.isVisible() == False:
            self.viewImage3 = viewImage("../output/ET_Cyclone/"+self.model_name+"/Stripes_3.png",'Stripes - 3')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage3.show()

    def openweek7_8(self):
        if self.viewImage4 == None or self.viewImage4.isVisible() == False:
            self.viewImage4 = viewImage("../output/ET_Cyclone/"+self.model_name+"/Stripes_4.png",'Stripes - 4')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage4.show()
    def openweek5(self):
        if self.viewImage5 == None or self.viewImage5.isVisible() == False:
            self.viewImage5 = viewImage("../output/ET_Cyclone/"+self.model_name+"/Stripes_1.png",'Stripes - 5')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage5.show()
    def openweek6(self):
        if self.viewImage6 == None or self.viewImage6.isVisible() == False:
            self.viewImage6 = viewImage("../output/ET_Cyclone/"+self.model_name+"/Stripes_1.png",'Stripes - 6')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage6.show()
    def openweek7(self):
        if self.viewImage7 == None or self.viewImage7.isVisible() == False:
            self.viewImage7 = viewImage("../output/ET_Cyclone/"+self.model_name+"/Stripes_1.png",'Stripes - 7')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage7.show()
    def openweek8(self):
        if self.viewImage8 == None or self.viewImage8.isVisible() == False:
            self.viewImage8 = viewImage("../output/ET_Cyclone/"+self.model_name+"/Stripes_1.png",'Stripes - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage8.show()


class seventhResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.viewImage1 = None
        self.viewImage2 = None
        self.viewImage3 = None
        self.viewImage4 = None
        self.model_name = dict_file['model name']
        self.setWindowTitle('Histogram of 10 hPa zonal wind results')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)

        #Create the weather image widget
        
        week1_2 = QPushButton('Week1 - 2', self)
        week1_2.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week1_2.clicked.connect(self.openweek1_2)

        week3_4 = QPushButton('Week3 - 4', self)
        week3_4.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week3_4.clicked.connect(self.openweek3_4)

        
        week5_6 = QPushButton('Week5 - 6', self)
        week5_6.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week5_6.clicked.connect(self.openweek5_6)

        week7_8 = QPushButton('Week7 - 8', self)
        week7_8.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week7_8.clicked.connect(self.openweek7_8)
       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(week1_2,alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(week3_4,alignment=Qt.AlignCenter)
        
        ryt_layout.addWidget(week5_6,alignment=Qt.AlignCenter)
        ryt_layout.addStretch()
        ryt_layout.addWidget(week7_8,alignment=Qt.AlignCenter)
        
        

        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()

    def openweek1_2(self):
        if self.viewImage1 == None or self.viewImage1.isVisible() == False:
            
            self.viewImage1 = viewImage("../output/Zonal_Wind_Hist/"+self.model_name+"/Stripes_1.png",'Stripes - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage1.show()

    def openweek3_4(self):
        if self.viewImage2 == None or self.viewImage2.isVisible() == False:
            
            self.viewImage2 = viewImage("../output/Zonal_Wind_Hist/"+self.model_name+"/Stripes_2.png",'Stripes - 2')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage2.show()
    def openweek5_6(self):
        if self.viewImage3 == None or self.viewImage3.isVisible() == False:
            
            self.viewImage3 = viewImage("../output/Zonal_Wind_Hist/"+self.model_name+"/Stripes_3.png",'Stripes - 3')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage3.show()
    def openweek7_8(self):
        if self.viewImage4 == None or self.viewImage4.isVisible() == False:
            self.viewImage4 = viewImage("../output/Zonal_Wind_Hist/"+self.model_name+"/Stripes_4.png",'Stripes - 4')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage4.show()

class fifthResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.viewImage1 = None
        self.viewImage2 = None
        self.viewImage3 = None
        self.viewImage4 = None
        self.model_name = dict_file['model name']
        self.setWindowTitle('Relative amplitude over PNA results')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)

        #Create the weather image widget
        
        week1_2 = QPushButton('PNA res - 1', self)
        week1_2.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week1_2.clicked.connect(self.openweek1_2)

        week3_4 = QPushButton('PNA res - 2', self)
        week3_4.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week3_4.clicked.connect(self.openweek3_4)


       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(week1_2,alignment=Qt.AlignCenter)
        layout.addStretch()
        ryt_layout.addWidget(week3_4,alignment=Qt.AlignCenter)
        ryt_layout.addStretch()

        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()

    def openweek1_2(self):
        if self.viewImage1 == None or self.viewImage1.isVisible() == False:
            
            self.viewImage1 = viewImage("../output/PNA_RelAmp/"+self.model_name+"/Stripes_1.png",'Stripes - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage1.show()

    def openweek3_4(self):
        if self.viewImage2 == None or self.viewImage2.isVisible() == False:
            
            self.viewImage2 = viewImage("../output/PNA_RelAmp/"+self.model_name+"/Stripes_2.png",'Stripes - 2')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage2.show()
    def openweek5_6(self):
        if self.viewImage3 == None or self.viewImage3.isVisible() == False:
            
            self.viewImage3 = viewImage("../output/PNA_RelAmp/"+self.model_name+"/Stripes_3.png",'Stripes - 3')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage3.show()
    def openweek7_8(self):
        if self.viewImage4 == None or self.viewImage4.isVisible() == False:
            self.viewImage4 = viewImage("../output/PNA_RelAmp/"+self.model_name+"/Stripes_4.png",'Stripes - 4')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage4.show()

class sixthResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.viewImage1 = None
        self.viewImage2 = None
        self.viewImage3 = None
        self.viewImage4 = None
        self.model_name = dict_file['model name']
        self.setWindowTitle('Stratospheric pathway')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)

        #Create the weather image widget
        
        week1_2 = QPushButton('Week1 - 2', self)
        week1_2.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week1_2.clicked.connect(self.openweek1_2)

        week3_4 = QPushButton('Week3 - 4', self)
        week3_4.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week3_4.clicked.connect(self.openweek3_4)

        
        week5_6 = QPushButton('Week5 - 6', self)
        week5_6.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week5_6.clicked.connect(self.openweek5_6)

        week7_8 = QPushButton('Week7 - 8', self)
        week7_8.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week7_8.clicked.connect(self.openweek7_8)
       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(week1_2,alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(week3_4,alignment=Qt.AlignCenter)
        
        ryt_layout.addWidget(week5_6,alignment=Qt.AlignCenter)
        ryt_layout.addStretch()
        ryt_layout.addWidget(week7_8,alignment=Qt.AlignCenter)
        
        

        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()
    def openweek1_2(self):
        if self.viewImage1 == None or self.viewImage1.isVisible() == False:
            
            self.viewImage1 = viewImage("../output/Strat_Path/"+self.model_name+"/Stripes_1.png",'Stripes - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage1.show()

    def openweek3_4(self):
        if self.viewImage2 == None or self.viewImage2.isVisible() == False:
            
            self.viewImage2 = viewImage("../output/Strat_Path/"+self.model_name+"/Stripes_2.png",'Stripes - 2')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage2.show()
    def openweek5_6(self):
        if self.viewImage3 == None or self.viewImage3.isVisible() == False:
            
            self.viewImage3 = viewImage("../output/Strat_Path/"+self.model_name+"/Stripes_3.png",'Stripes - 3')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage3.show()
    def openweek7_8(self):
        if self.viewImage4 == None or self.viewImage4.isVisible() == False:
            self.viewImage4 = viewImage("../output/Strat_Path/"+self.model_name+"/Stripes_4.png",'Stripes - 4')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage4.show()

    
class third2Result(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.viewImage1 = None
        self.viewImage2 = None
        self.viewImage3 = None
        self.viewImage4 = None
        self.model_name = dict_file['model name']
        self.setWindowTitle('Pattern CC over the Euro-Atlantic sector')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)

        #Create the weather image widget
        
        week1_2 = QPushButton('Euro-Atlantic sector - 1', self)
        week1_2.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week1_2.clicked.connect(self.openweek1_2)

        week3_4 = QPushButton('Euro-Atlantic sector - 2', self)
        week3_4.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week3_4.clicked.connect(self.openweek3_4)

       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(week1_2,alignment=Qt.AlignCenter)
        layout.addStretch()
        ryt_layout.addWidget(week3_4,alignment=Qt.AlignCenter)
        ryt_layout.addStretch()
        
        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()

    def openweek1_2(self):
        if self.viewImage1 == None or self.viewImage1.isVisible() == False:
            
            self.viewImage1 = viewImage("../output/StripeIndexGeoPotHeight/"+self.model_name+"/Stripes_1.png",'Stripes - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage1.show()

    def openweek3_4(self):
        if self.viewImage2 == None or self.viewImage2.isVisible() == False:
            
            self.viewImage2 = viewImage("../output/PatternCC_Atlantic/"+self.model_name+"/Stripes_2.png",'Stripes - 2')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage2.show()
    def openweek5_6(self):
        if self.viewImage3 == None or self.viewImage3.isVisible() == False:
            
            self.viewImage3 = viewImage("../output/PatternCC_Atlantic/"+self.model_name+"/Stripes_3.png",'Stripes - 3')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage3.show()
    def openweek7_8(self):
        if self.viewImage4 == None or self.viewImage4.isVisible() == False:
            self.viewImage4 = viewImage("../output/PatternCC_Atlantic/"+self.model_name+"/Stripes_4.png",'Stripes - 4')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage4.show()

class fourthResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.viewImage1 = None
        self.viewImage2 = None
        self.viewImage3 = None
        self.viewImage4 = None
        self.model_name = dict_file['model name']
        self.setWindowTitle('Fraction of the observed STRIPE index for geopotential height results')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)

        #Create the weather image widget
        
        week1_2 = QPushButton('Week1 - 2', self)
        week1_2.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week1_2.clicked.connect(self.openweek1_2)

        week3_4 = QPushButton('Week3 - 4', self)
        week3_4.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week3_4.clicked.connect(self.openweek3_4)

        
        week5_6 = QPushButton('Week5 - 6', self)
        week5_6.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week5_6.clicked.connect(self.openweek5_6)

        week7_8 = QPushButton('Week7 - 8', self)
        week7_8.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week7_8.clicked.connect(self.openweek7_8)
       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(week1_2,alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(week3_4,alignment=Qt.AlignCenter)
        
        ryt_layout.addWidget(week5_6,alignment=Qt.AlignCenter)
        ryt_layout.addStretch()
        ryt_layout.addWidget(week7_8,alignment=Qt.AlignCenter)
        
        

        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()

    def openweek1_2(self):
        if self.viewImage1 == None or self.viewImage1.isVisible() == False:
            
            self.viewImage1 = viewImage("../output/StripesFraction/"+self.model_name+"/Stripes_1.png",'Stripes - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage1.show()

    def openweek3_4(self):
        if self.viewImage2 == None or self.viewImage2.isVisible() == False:
            
            self.viewImage2 = viewImage("../output/StripesFraction/"+self.model_name+"/Stripes_2.png",'Stripes - 2')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage2.show()
    def openweek5_6(self):
        if self.viewImage3 == None or self.viewImage3.isVisible() == False:
            
            self.viewImage3 = viewImage("../output/StripesFraction/"+self.model_name+"/Stripes_3.png",'Stripes - 3')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage3.show()
    def openweek7_8(self):
        if self.viewImage4 == None or self.viewImage4.isVisible() == False:
            self.viewImage4 = viewImage("../output/StripesFraction/"+self.model_name+"/Stripes_4.png",'Stripes - 4')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage4.show()


class firstResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.model_name = dict_file['model name']
        self.viewImage1 = None
        self.viewImage2 = None
        self.viewImage3 = None
        self.viewImage4 = None
        self.setWindowTitle('STRIPES Index for geopotential height')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)
        directory_path = f'../output/T2m/{self.model_name}'
        #Create the weather image widget
        all_files = os.listdir(directory_path)
        file_list = [file for file in all_files if os.path.isfile(os.path.join(directory_path, file))]
        
        
        week1_2 = QPushButton('Week1 - 2', self)
        week1_2.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week1_2.clicked.connect(self.openweek1_2)

        week3_4 = QPushButton('Week3 - 4', self)
        week3_4.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week3_4.clicked.connect(self.openweek3_4)

        
        week5_6 = QPushButton('Week5 - 6', self)
        week5_6.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week5_6.clicked.connect(self.openweek5_6)

        week7_8 = QPushButton('Week7 - 8', self)
        week7_8.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week7_8.clicked.connect(self.openweek7_8)

       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(week1_2,alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(week3_4,alignment=Qt.AlignCenter)
        
        ryt_layout.addWidget(week5_6,alignment=Qt.AlignCenter)
        ryt_layout.addStretch()
        ryt_layout.addWidget(week7_8,alignment=Qt.AlignCenter)
        
        

        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)
    
    

    def closee(self):
        self.close()
        self.parent.show()
    def openweek1_2(self):
        if self.viewImage1 == None or self.viewImage1.isVisible() == False:
            
            self.viewImage1 = viewImage("../output/StripesGeopot/"+self.model_name+"/Stripes_1.png",'Stripes - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage1.show()

    def openweek3_4(self):
        if self.viewImage2 == None or self.viewImage2.isVisible() == False:
            
            self.viewImage2 = viewImage("../output/StripesGeopot/"+self.model_name+"/Stripes_2.png",'Stripes - 2')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage2.show()
    def openweek5_6(self):
        if self.viewImage3 == None or self.viewImage3.isVisible() == False:
            
            self.viewImage3 = viewImage("../output/StripesGeopot/"+self.model_name+"/Stripes_3.png",'Stripes - 3')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage3.show()
    def openweek7_8(self):
        if self.viewImage4 == None or self.viewImage4.isVisible() == False:
            self.viewImage4 = viewImage("../output/StripesGeopot/"+self.model_name+"/Stripes_4.png",'Stripes - 4')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage4.show()

class secondResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.viewImage1 = None
        self.viewImage2 = None
        self.viewImage3 = None
        self.viewImage4 = None
        self.model_name = dict_file['model name']
        self.setWindowTitle('STRIPES Index for precipitation')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)

        #Create the weather image widget
        
        week1_2 = QPushButton('Week1 - 2', self)
        week1_2.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week1_2.clicked.connect(self.openweek1_2)

        week3_4 = QPushButton('Week3 - 4', self)
        week3_4.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week3_4.clicked.connect(self.openweek3_4)

        
        week5_6 = QPushButton('Week5 - 6', self)
        week5_6.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week5_6.clicked.connect(self.openweek5_6)

        week7_8 = QPushButton('Week7 - 8', self)
        week7_8.setFixedSize(100,30)
        #button2.setGeometry(200, 150, 40, 40)
        week7_8.clicked.connect(self.openweek7_8)
       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(week1_2,alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(week3_4,alignment=Qt.AlignCenter)
        
        ryt_layout.addWidget(week5_6,alignment=Qt.AlignCenter)
        ryt_layout.addStretch()
        ryt_layout.addWidget(week7_8,alignment=Qt.AlignCenter)
        
        

        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()

    def openweek1_2(self):
        if self.viewImage1 == None or self.viewImage1.isVisible() == False:
            
            self.viewImage1 = viewImage("../output/StripesPrecip/"+self.model_name+"/Stripes_1.png",'Stripes - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage1.show()

    def openweek3_4(self):
        if self.viewImage2 == None or self.viewImage2.isVisible() == False:
            
            self.viewImage2 = viewImage("../output/StripesPrecip/"+self.model_name+"/Stripes_2.png",'Stripes - 2')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage2.show()
    def openweek5_6(self):
        if self.viewImage3 == None or self.viewImage3.isVisible() == False:
            
            self.viewImage3 = viewImage("../output/StripesPrecip/"+self.model_name+"/Stripes_3.png",'Stripes - 3')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage3.show()
    def openweek7_8(self):
        if self.viewImage4 == None or self.viewImage4.isVisible() == False:
            self.viewImage4 = viewImage("../output/StripesPrecip/"+self.model_name+"/Stripes_4.png",'Stripes - 4')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage4.show()

class thirdResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.viewImage1 = None
        self.viewImage2 = None
        self.viewImage3 = None
        self.viewImage4 = None
        self.model_name = dict_file['model name']
        self.setWindowTitle('Pattern CC over the PNA region')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)

        #Create the weather image widget
        
        week1_2 = QPushButton('PNA region - 1', self)
        week1_2.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week1_2.clicked.connect(self.openweek1_2)

        week3_4 = QPushButton('PNA region - 2', self)
        week3_4.setFixedSize(200,30)
        #button2.setGeometry(200, 150, 40, 40)
        week3_4.clicked.connect(self.openweek3_4)
       
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(week1_2,alignment=Qt.AlignCenter)
        layout.addStretch()
        ryt_layout.addWidget(week3_4,alignment=Qt.AlignCenter)
        ryt_layout.addStretch()
      
        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
        #Create a layout for the right half (text widgets and button)
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")

        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        # Create a central widget to hold the splitter
        main_widget = QWidget()

        
        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)
        back.setStyleSheet("""
        QPushButton:hover {
            background-color: gray;
        }
    """)
        central_layout.addWidget(back,alignment=Qt.AlignCenter)
        main_widget.setLayout(central_layout)
        self.setCentralWidget(main_widget)

    def closee(self):
        self.close()
        self.parent.show()
    def openweek1_2(self):
        if self.viewImage1 == None or self.viewImage1.isVisible() == False:
            
            self.viewImage1 = viewImage("../output/PatternCC_PNA/"+self.model_name+"/Stripes_1.png",'Stripes - 1')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage1.show()

    def openweek3_4(self):
        if self.viewImage2 == None or self.viewImage2.isVisible() == False:
            
            self.viewImage2 = viewImage("../output/PatternCC_PNA/"+self.model_name+"/Stripes_2.png",'Stripes - 2')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage2.show()
    def openweek5_6(self):
        if self.viewImage3 == None or self.viewImage3.isVisible() == False:
            
            self.viewImage3 = viewImage("../output/PatternCC_PNA/"+self.model_name+"/Stripes_3.png",'Stripes - 3')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage3.show()
    def openweek7_8(self):
        if self.viewImage4 == None or self.viewImage4.isVisible() == False:
            self.viewImage4 = viewImage("../output/PatternCC_PNA/"+self.model_name+"/Stripes_4.png",'Stripes - 4')
            #self.viewImage1.closed.connect(self.quit1)
            self.viewImage4.show()


class viewImage(QMainWindow):
    def __init__(self,imageP,title):
        super().__init__()
        imageP = os.path.abspath(imageP)
        self.setWindowTitle(title)
        self.setGeometry(200, 0, 800, 800)  # Set window position and size
        self.closed = pyqtSignal()
        #scroll_bar = QScrollBar(self)
        self.scroll = QScrollArea()
        #Create the weather image widget
        image = QLabel(self)
        pixmap = QPixmap(imageP) 
        pixmap= pixmap.scaled(450, 700,Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image.setPixmap(pixmap)
        
        image.setAlignment(Qt.AlignCenter)
        self.imagep = imageP
        left_layout = QVBoxLayout()
        left_layout.addWidget(image)
        left_layout.addStretch()
        
        right_layout = QVBoxLayout()
        helpText = QLabel('Here will be the help text on this image.')

        download = QPushButton('Download image', self)
        download.setFixedSize(300,30)
        download.clicked.connect(self.download_image)

        right_layout.addWidget(helpText)
        right_layout.addStretch()
        right_layout.addWidget(download)
        
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
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(central_widget)
        #central_widget.setLayout(glayout)
        self.setCentralWidget(self.scroll)
    def download_image(self):
         # Replace with the image URL you want to download
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Specify the relative path to the image file
        relative_path = self.imagep # Adjust the relative path as needed

        # Construct the source path by joining the script directory and relative path
        source_path = os.path.join(script_directory, relative_path)

        if not source_path:
            return

        destination_path, _ = QFileDialog.getSaveFileName(self, "Save Image As", "", "Images (*.jpg *.png);;All Files (*)", options=QFileDialog.ReadOnly)

        if destination_path:
            try:
                shutil.copy(source_path, destination_path)
            except Exception as e:
            
                print("Failed to download the image.")
        

    



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
            path = '../output/StripeIndexGeoPotHeight/Stripes_'+str(i+1)+'.png'
            px1 = QPixmap(path)
            #px1.setDevicePixelRatio(0.5)
            stripes.append(px1)

        for i in range(4):
            image = QLabel(self)
            image.setPixmap(stripes[i].scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            glayout.addWidget(image,0,i)

        '''weather_image = QLabel(self)
        pixmap = QPixmap('weather.jpg') 
        '''
        central_widget.setLayout(glayout)
        #Replace with the actual path to your weather image file
        #Scale the pixmap to fit the size of the QLabel
        #pixmap = pixmap.scaled(weather_image.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        '''weather_image.setPixmap(pixmap)
        weather_image.resize(pixmap.width(),pixmap.height())'''
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
    style = """
        QScrollBar:horizontal {              
          border: none;
          height: 10px;
          margin: 0px 0px 0px 0px;
        }
            QWidget#left { 
            border-width: 3px; border-style: solid; border-color: black white black black; 
            }
            QWidget#right { 
            border-width: 3px; border-style: solid; border-color: black white black black; 
            }
        QScrollBar {
                width: 12px;
            }
            QScrollBar::handle {
                background: darkgray;
                border: 2px solid gray;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::add-line {
                background: none;
                height: 10px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line {
                background: none;
                height: 10px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
        QWidget{
            background: #262D37;
        }
        
        QLabel{
            color: #fff;
        }

        QLabel#round_count_label, QLabel#highscore_count_label{
            border: 1px solid #fff;
            border-radius: 8px;
            padding: 2px;
            font-size: 10pt;
        }
        QPushButton
        {
            color: white;
            background: #0577a8;
            border: 1px #DADADA solid;
            padding: 5px 10px;
            border-radius: 2px;
            font-weight: bold;
            outline: none;
        }
        
        QRadioButton,QCheckBox{
            color:white;
            font-weight: bold;
        }
        QRadioButton::indicator, QCheckBox::indicator{
        background-color: white; 
        border: 2px solid white;
        border-radius: 6px;
        width: 10px; 
        height: 10px;
    }
    QCheckBox::indicator
    {
    border-radius: 50%;
    }
    QCheckBox::indicator:checked
    {
    border-image : url(check.png);
    }
    QRadioButton::indicator:checked, QCheckBox::indicator:checked {
        background-color: gray; /* Change background color when checked */
    }
        QPushButton:hover{
            border: 1px #C6C6C6 solid;
            color: #fff;
            background: #0892D0;
        }
        QLineEdit {
            padding: 1px;
            color: #fff;
            border-style: solid;
            border: 2px solid #fff;
            border-radius: 8px;
        }

    """
    app.setStyleSheet(style)
    file_path = "../output/models.txt"
    models=[]
    with open(file_path, "r") as file:
        for line in file:
            models.append(line)
            models[-1]=models[-1][:-1].lower()
    entry_window = FirstWindow()
    entry_window.show()
    sys.exit(app.exec())

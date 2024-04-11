from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QDialog, QSplitter, QSizePolicy
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QPixmap
import yaml
from PyQt5.QtCore import QObject, QThread, QRunnable
import os
import time, sys
import subprocess
import shutil
class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MJO Teleconnections Diagnostics')
        self.setGeometry(200, 100, 800, 400) #position and size
        self.show()
        self.setStyleSheet("QMainWindow{background: #262D37;color: #fff;}")
        ## Logo widget
        logo_image = QLabel(self)
        pixmap = QPixmap('logo1.jpg') 
        logo_image.setPixmap(pixmap)
        logo_image.resize(pixmap.width(),pixmap.height())
        #Set the size policy of the QLabel to expand and fill the available space
        logo_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        logo_image.setAlignment(Qt.AlignCenter)
        
        ## Welcome label
        welcome_label = QLabel('Welcome to MJO Teleconnections Diagnostics', self)
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("QLabel { font-weight: bold; color: white; }")
        
        ## Start button
        start = QPushButton('Start', self)
        start.setFixedSize(70,30)
        #start.setGeometry(200, 150, 40, 40)
        start.clicked.connect(self.open_ViewRes_RunCal_window)
        
        ## Layout
        layout = QVBoxLayout()
        layout.addWidget(welcome_label)
        layout.addStretch()
        layout.addWidget(logo_image)
        layout.addStretch()
        layout.addWidget(start,alignment=Qt.AlignCenter)
        layout.addStretch()
        
        ## Central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.open_ViewRes_RunCal_window()
    def open_ViewRes_RunCal_window(self):
        self.ViewRes_RunCal_window = ViewRes_RunCal(self)
        self.hide()
    
diagnostics_dir={'stripesgeopot':1,'stripesprecip':2,'patterncc_pna':3,'patterncc_atlantic':4,'strat_path':5,'zonal_wind_hist':6,'et_cyclone':7,'mjo':8,'t2m':9}


def list_folders(path):
    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    return folders
def get_model_diagnostics(model_name):
    start_path = '../output/'
    all_folders = list_folders(start_path)
    diags=[]
    for f in all_folders:
        if f.lower() in diagnostics_dir:
            fm_path = os.path.join(start_path,f, model_name)
            # Check if the item is a directory of the diagnostics we know
            print(fm_path)
            if os.path.isdir(fm_path):
                #print('path exists',fm_path)
                diags.append(diagnostics_dir[f.lower()])
            
    if diags == []:
        return None, None
    return model_name,diags
            
        
class ViewRes_RunCal(QMainWindow):
    def __init__(self,parent):
        super().__init__()
        self.dict_file={}
        self.parent = parent
        self.setWindowTitle('MJO Teleconnections Diagnostics')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        self.show()
        
        ## View Result button
        ViewRes= QPushButton('View results from previous calculations', self)
        ViewRes.setFixedSize(300,30)
        ViewRes.clicked.connect(self.showInputDialog)
        
        ## Run Dialog button
        runDiag = QPushButton('Run diagnostics first', self)
        runDiag.setFixedSize(300,30)
        #button2.setGeometry(200, 150, 40, 40)
        runDiag.clicked.connect(self.openrunDiag)
       
        ## back button to start window
        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)
        
        ## Layouts
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
       
        layout.addWidget(ViewRes,alignment=Qt.AlignCenter)
        layout.addStretch()
        
        ryt_layout.addWidget(runDiag,alignment=Qt.AlignCenter)
        ryt_layout.addStretch()
        
        ## Frames
        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
     
        frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        ryt_frame.setStyleSheet("QFrame { border-width: 2px; border-style: solid; border-color: black white black black; }")
        
        # Horizontal layout for frames
        lay = QHBoxLayout()
        lay.addWidget(frame)
        lay.addWidget(ryt_frame)
        central_widget = QWidget()
        central_widget.setLayout(lay)

        fr = QFrame()
        fr.setLayout(lay)
        main_widget = QWidget()

        central_layout = QVBoxLayout()
        central_layout.addWidget(fr)

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
        modelname_exists=0
        while True:
            dialog = InputDialog()
            result = dialog.exec_()
            if result == QDialog.Accepted:
                #print('When enter or ok button is clicked')
                self.model_name = dialog.input_text.text()
                if len(self.model_name)>0:
                    self.model_name,self.selected = get_model_diagnostics(self.model_name)
                    if self.model_name: 
                        self.dict_file['model name'] = self.model_name
                        #print(f"Accepted: {self.model_name}")
                        modelname_exists=1
                        break  # Break the loop when valid input is provided
                    else:
                        self.showErrorMessage("There is no model with this name.")
                else:
                    self.showErrorMessage("Empty text")
            else:
                #print("Exiting dialog box")
                break  # Break the loop if the user cancels the input dialog
                
        if modelname_exists==1:
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
        self.setGeometry(400, 220, 300, 100)

    def initUI(self):
        layout = QVBoxLayout()
        self.input_label = QLabel('Enter the model name:')
        self.input_text = QLineEdit()
        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setFixedSize(70,30)
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_text)
        layout.addWidget(self.ok_button,alignment=Qt.AlignCenter)
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


        help_label = QLabel('''
The MJO-Diagnostics Package computes metrics that require the meteorological fields listed below. User must prepare their files (one variable per file) using the name and units listed in parenthesis. Meterological fields can be either total fields or anomalies.
----------------------------------------------------
 Meteorological parameters:
----------------------------------------------------
* Geopotential at 500mb an 100mb:
*** Variable can be named any of: 'z', 'Z', 'gh', 'z500'
*** Unit can be any of:'m**2 s**-2', 'm^2/s^2', 'm2/s2','m2s-2', 'm2 s-2'
* Precipitation rate:
*** Variable can be named any of: 'prate', 'precipitationCal','pr','precip'
*** Unit: mm/day
* Zonal and meridional winds at 850mb
* Zonal wind at 10mb
* Meridional wind at 500mb
* Air temperature at 100mb 
* 2-metre Temperature:
*** Variable can be named any of: 't2m', 'T2m', 'temp'
*** Unit: K

To run the package, the user needs to specify: 
* DIR_IN: the path of the directory (e.g., /project/$user) containing all input data including forecast and verification data. If the user downloads the ERA-Interim dataset made available with the Package the directory 'mjo_teleconnections_data/' must be located here. 

* START_DATE: the start date of forecast data in the format YYYYMMDD 

* END_DATE: the last date of forecast data in the format YYYYMMDD  

* Length of the forecats (in days): number of forecast leads  

* Number of ensembles: ensemble members  

* Number of initial dates: the number of initial conditions for the forecasts
                         - if the forecast is initialized, for example 2 times month enter 2
                         - if the forecast is initialized on particular days of the week, enter 1

* Initial dates: days of initialization in the format D or DD
               - if the forecast is initialized 2 times a month, for example on the 1st and 15th, enter 1 15 

*Use ERA_I for validation: 
                        - Select 'Yes' (default) if ERA-Interim dataset provided with the package is used for verification (dataset must be downloaded in placed in the 'DIR_IN/mjo_teleconnections_data/erai')
                        - Select 'No' if user provided dataset will be used for verification(user verification dataset must be placed in the directory 'DIR_IN/OBS')

*Use IMERG for validation: 
                        - Select 'Yes' (default) if IMERG dataset provided with the package is used for verification (datset must be downloaded in placed in the directory 'DIR_IN/mjo_teleconnections_data/imerg')
                        - Select 'No' if user provided dataset will be used for verification (user verification dataset must be placed in the directory 'DIR_IN/OBS')




''')
        help_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Create the text widgets
        help_label.setWordWrap(True) 
        dir_in_label = QLabel('DIR_IN:', self)
        self.dir_in_text = QLineEdit(self)
        start_date_label = QLabel('START_DATE:', self)
        self.start_date_text = QLineEdit(self)

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
        button2.clicked.connect(self.open_modelInformation_window)
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
        vbox.addWidget(self.imerg_yes )
        self.imerg_no = QRadioButton("No")
        vbox.addWidget(self.imerg_no)
        

        #Create a layout for the left half (Help text label)
        left_layout = QVBoxLayout()
        left_layout.addStretch()
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

        # Set the right layout to the stripesprecip widget of the splitter
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

    
    def open_modelInformation_window(self):
        if self.dir_in_text.text() == '':
            QMessageBox.warning(self,'Missing fields!',"Please enter the input directory")
            return 
        if  self.start_date_text.text() == '':
            QMessageBox.warning(self,'Missing fields!',"Please enter the start date")
            return 
        if self.end_date_text.text() == '':
            QMessageBox.warning(self,'Missing fields!',"Please enter the end date")
            return 
        if self.lengthFor_text.text() == '':
            QMessageBox.warning(self,'Missing fields!',"Please enter the length of forecasts.")
            return 
        if self.num_ensm.text() == '':
            QMessageBox.warning(self,'Missing fields!',"Please enter the number of ensembles")
            return
        if self.initial_dates.text() == '':
            QMessageBox.warning(self,'Missing fields!',"Please enter the number of initial dates ")
            return
        if self.initial_dates_values.text() == '':
            QMessageBox.warning(self,'Missing fields!',"Please enter the initial dates ")
            return
        num_exp = int(self.initial_dates.text())
        num_given = len(list(map(int,self.initial_dates_values.text().split())))
        if num_exp != num_given:
            QMessageBox.warning(self,"Number of initial dates should match the give number","Please enter "+str(num_exp)+" initial date(s)")
            return
        dict_file=self.dict_file
        dict_file['DIR_IN'] = self.dir_in_text.text()
        dict_file['START_DATE']= self.start_date_text.text()
        dict_file['END_DATE']= self.end_date_text.text()
        dict_file['length of forecasts'] = self.lengthFor_text.text()
        dict_file['Number of ensembles'] = self.num_ensm.text()
        dict_file['Number of initial dates']= int(self.initial_dates.text())
        dict_file['Initial dates' ]= list(map(int,self.initial_dates_values.text().split()))
        ##print(type(self.initial_dates_values.text()),' has values ',list(map(int,self.initial_dates_values.text().split())))
        dict_file['ERAI'] = self.era_yes.isChecked()
        dict_file['IMERG'] = self.imerg_yes.isChecked()
        self.modelInformation_window = modelInformation(self,self.dir_in_text.text(),dict_file['ERAI'],dict_file)
        self.modelInformation_window.showMaximized()
        self.hide()
    def closee(self):
        self.close()
        self.parent.show()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.open_modelInformation_window()

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
The package can be applied to one forecast model. The name of the model will apear on the figures and will be required when the package is used to display existing results.

* Model name: enter the model name, e.g., UFS or ufs
 
* Model initial conditions: 
                    - Select 'Yes' if model data include the initial conditions (forecast hour 00Z) 
                    - Select 'No' if model data do not include the initial conditions

* Smooth climatology:
                  - Select 'Yes' only for the CNRM model version CM6.1 (S2S database), EMC, ESRL, and NRL models (SubX or SubC project), and models that are initialized on the the same day of the week (e.g., Wednesday)
                  - Select 'No' for most models in the S2S database


                            ''')
        help_label.setWordWrap(True)
        #Model name
        model_label = QLabel('Model name:', self)
        self.model_name = QLineEdit(self)

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
        self.button2.clicked.connect(self.open_stripesprecip_window)
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
        #right_layout.addWidget(daily_mean_values_label)
        #right_layout.addWidget(groupbox)
        
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

        # Set the right layout to the stripesprecip widget of the splitter
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
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.open_stripesprecip_window()

    def open_stripesprecip_window(self):
        #commenting out the input validation
        dict_file =self.dict_file
        dict_file['model name'] = self.model_name.text()
        dict_file['model initial conditions']= self.initial_conds_yes.isChecked()
        dict_file['smooth climatology'] = self.smooth_climatology_yes.isChecked()
        
        self.dict_file = dict_file
        
        self.stripesprecip_window = stripesprecipWindow(self,self.dir_in_text,self.era,dict_file)
        self.stripesprecip_window.showMaximized()
        self.hide()
    

    def closee(self):
        self.close()
        self.parent.show()




class stripesprecipWindow(QMainWindow):
    def __init__(self,parent,dirin,era,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.scroll = QScrollArea()
        self.parent=parent
        self.dict_file = dict_file
        self.setWindowTitle('Daily Anomaly and RMM')
        self.setGeometry(0, 0, 800, 400)  # Set window position and size
        self.showMaximized()
        
        self.era = era

        help_label = QLabel('''
       


* Compute daily anomalies:
                    - Select 'Yes' if forecast data is provided as daily mean values
                    - Select 'No' if forecast data is provided as daily anomaly values

* Compute the RMM index: The selction of MJO events is based on the amplitude and phases of the MJO RMM index (Wheeler and Hendon, 1984). The package includes the amplitude and phases of the RMM index computed using the ERA-Interim and NOAA OLR data for the period 01/01/1979-08/31/2019. 
    - Select 'No' to use the RMM index included in the Package
    - Select 'Yes' to compute the RMM index using new datasets; the user is required to provide the paths of these datasets, which must be staged in 'DIR_IN/OBS'
                            ''')
        help_label.setWordWrap(True)
       
        #Scale the pixmap to fit the size of the QLabel
        #pixmap = pixmap.scaled(weather_image.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
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
        but.clicked.connect(self.openSelectDiagWindow)

        

        self.dirin = dirin
        prefix = self.dirin+"/OBS/"
        
        #change labels correctly.
        dir_in_label = QLabel('Path to OLR observation data files:', self)
        self.olrDataFiles = QLineEdit(self)
        self.olrDataFiles.setText(prefix)
        self.olrDataFiles.setCursorPosition(len(prefix))

        zonalpath = QLabel('Path to zonal wind at 850 hPa observation data files:', self)
        self.zonalpathT  = QLineEdit(self)
        self.zonalpathT.setText(prefix)
        self.zonalpathT.setCursorPosition(len(prefix))
        

        zonalpath200 = QLabel('Path to zonal wind at 200 hPa observation data files:', self)
        self.zonalpath200T = QLineEdit(self)
        self.zonalpath200T.setText(prefix)
        self.zonalpath200T.setCursorPosition(len(prefix))

        but = QPushButton('Next', self)
        but.setFixedSize(70,30)
        but.clicked.connect(self.openSelectDiagWindow)

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

        # Set the right layout to the stripesprecip widget of the splitter
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
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.openSelectDiagWindow() 
        
    
    def onrmmClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            self.rmm = True
            self.right_layout.insertWidget(4,self.groupbox)
            self.right_layout.addStretch()
        else:
            self.rmm = False
            self.groupbox.setParent(None)


    def openSelectDiagWindow(self):
        dict_file=self.dict_file
        if self.dailyAnomaly:
            dict_file['Daily Anomaly'] = True
        else:
            dict_file['Daily Anomaly'] = False
        dict_file['RMM'] = self.rmm
        
        dict_file['Path to OLR observation data files'] = self.olrDataFiles.text()
        dict_file['Path to zonal wind at 850 hPa observation data files'] = self.zonalpathT.text()
        dict_file['Path to zonal wind at 200 hPa observation data files'] = self.zonalpath200T.text()

        
        self.third_window = SelectDiagWindow(self,self.dirin,self.era,dict_file)
        self.third_window.showMaximized()
        self.hide()
        
        #self.close()

    def method(self,checked):
        # #printing the checked status
        if checked:
            self.right_layout.addWidget(self.groupbox)
            #self.right_layout.addStretch()
            
        else:
            self.groupbox.setParent(None)
            #self.close()




class SelectDiagWindow(QMainWindow):
    def __init__(self,parent,dirin,era,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent=parent
        self.dict_file = dict_file
        self.setWindowTitle('Select which diagnostic you want to run')
        self.setGeometry(0, 0, 800, 400)  # Set window position and size
        self.showMaximized()

        help_label = QLabel('''


On this page, the user can select all diagnostics, one diagnostic or multiple diagnostics. On the next page, the user will be prompted to provide additional information about the forecast data files required for each of the diagnostics.

* The Extratropical Cyclone Activity
    - Provides composites of 24-h difference filtered eddy kinetic energy at 850-hPa (computed using U850 and V850) and the spatial correlation coefficient between model and reanalysis composites ...

                            ''')
        help_label.setWordWrap(True)
        
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

        self.stripesgeopot = QCheckBox("STRIPES Index for geopotential height")
        self.stripesgeopot.setChecked(False)

        self.stripesprecip = QCheckBox("STRIPES Index for precipitation")
        self.stripesprecip.setChecked(False)

        self.patterncc_pna = QCheckBox("Pattern CC and Relative Amplitude over the PNA region")
        self.patterncc_pna.setChecked(False) #3

        self.patterncc_atlantic = QCheckBox("Pattern CC and Relative Amplitude over the Euro-Atlantic sector")
        self.patterncc_atlantic.setChecked(False) #4

        #self.fourth = QCheckBox("Fraction of the observed STRIPES index for geopotential height")
        #self.fourth.setChecked(False)

        #self.fifth = QCheckBox("Relative amplitude over PNA?")
        #self.fifth.setChecked(False)

        self.strat_path = QCheckBox("Stratospheric pathway")
        self.strat_path.setChecked(False)

        self.zonal_wind_hist = QCheckBox("Histogram of 10 hPa zonal wind")
        self.zonal_wind_hist.setChecked(False)

        self.et_cyclone = QCheckBox("Extratropical cyclone activity")
        self.et_cyclone.setChecked(False)

        #self.nine = QCheckBox("EKE850-Z500 correlation")
        #self.nine.setChecked(False)

        self.mjo = QCheckBox("MJO")
        self.mjo.setChecked(False) #8

        self.t2m = QCheckBox("Surface air temperature")
        self.t2m.setChecked(False)

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
        right_layout.addWidget(self.stripesgeopot)
        right_layout.addWidget(self.stripesprecip)
        right_layout.addWidget(self.patterncc_pna)
        right_layout.addWidget(self.patterncc_atlantic)
        #right_layout.addWidget(self.fourth)
        #right_layout.addWidget(self.fifth)
        right_layout.addWidget(self.strat_path)
        right_layout.addWidget(self.zonal_wind_hist)
        right_layout.addWidget(self.et_cyclone)
        #right_layout.addWidget(self.nine)
        right_layout.addWidget(self.mjo)
        right_layout.addWidget(self.t2m)
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
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.openThirdSubWindow()
    def openThirdSubWindow(self):
        selected=[]
        if(self.all.isChecked()):
            selected.append(0)
        else:
            if self.stripesgeopot.isChecked():
                selected.append(1)
            if self.stripesprecip.isChecked():
                selected.append(2)
            if self.patterncc_pna.isChecked():
                selected.append(3)
            if self.patterncc_atlantic.isChecked():
                selected.append(4)
            #if self.fourth.isChecked():
             #   selected.append(4)
            #if self.fifth.isChecked():
             #   selected.append(5)
            if self.strat_path.isChecked():
                selected.append(5)
            if self.zonal_wind_hist.isChecked():
                selected.append(6)
            if self.et_cyclone.isChecked():
                selected.append(7)
            #if self.nine.isChecked():
             #   selected.append(9)
            if self.mjo.isChecked():
                selected.append(8)
            if self.t2m.isChecked():
                selected.append(9)
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
        # #printing the checked status
        if checked:
            self.all.setChecked(True)
            self.stripesgeopot.setChecked(True)
            self.stripesprecip.setChecked(True)
            self.patterncc_pna.setChecked(True)
            self.patterncc_atlantic.setChecked(True)
            #self.fourth.setChecked(True)
            #self.fifth.setChecked(True)
            self.strat_path.setChecked(True)
            self.zonal_wind_hist.setChecked(True)
            self.et_cyclone.setChecked(True)
            #self.nine.setChecked(True)
            self.mjo.setChecked(True)
            self.t2m.setChecked(True)
        else:
            self.all.setChecked(False)
            self.stripesgeopot.setChecked(False)
            self.stripesprecip.setChecked(False)
            self.patterncc_pna.setChecked(False)
            self.patterncc_atlantic.setChecked(False)
            #self.fourth.setChecked(False)
            self.strat_path.setChecked(False)
            self.zonal_wind_hist.setChecked(False)
            self.et_cyclone.setChecked(False)
            #self.nine.setChecked(False)
            self.mjo.setChecked(False)
            self.t2m.setChecked(False)
    
     


class ThirdSubWindow(QMainWindow):
    def __init__(self,parent,selected,dirin,era,dict_file):
        super().__init__()
        
        #passed down variables
        self.parent=parent
        self.selected = selected
        self.era=era
        self.dirin = dirin
        self.pref = self.dirin+"/"
        self.prefix = self.dirin+"/OBS/"
        self.dict_file = dict_file
        #self.num_dates = dict_file['Number of initial dates:']
        self.dates = dict_file['Initial dates' ]
        
        #set window title and position and size
        self.setWindowTitle('Third Sub Window')
        self.setGeometry(0, 0, 800, 400)  
        self.showMaximized()
        
        #scroll bar - vertical and horizontal
        #scroll Area which contains the widgets, set as the centralWidget
        self.scroll = QScrollArea()  
        #self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        
        
        #right_layout declaration
        right_layout = QVBoxLayout()
        left_layout = QVBoxLayout()
        
        ##Path to Z500 data files:
        z500 = QLabel(f'Path to Z500 model data files:', self)
        self.z500T = QLineEdit(self)
        self.z500T.setText(self.pref)
        self.z500T.setCursorPosition(len(self.pref))
         
        #z500 obs data files:
        z500obs = QLabel(f'Path to Z500 observation data files:', self)
        self.z500Tobs = QLineEdit(self)
        self.z500Tobs.setText(self.prefix)
        self.z500Tobs.setCursorPosition(len(self.prefix))
        
        
        ##OLD data files
        dir_OLR_label = QLabel('Path to OLR model data files:', self)
        self.olrDataFiles = QLineEdit(self)
        self.olrDataFiles.setText(self.pref)
        self.olrDataFiles.setCursorPosition(len(self.pref))
        #OLD obs data files
        dir_OLR_label_obs = QLabel('Path to OLR observation data files:', self)
        self.olrobsDataFiles = QLineEdit(self)
        self.olrobsDataFiles.setText(self.prefix)
        self.olrobsDataFiles.setCursorPosition(len(self.prefix))

        
        '''#Path to Extratropical cyclone activity data files
        Ez500 = QLabel(f'Path to Z500 model data files for Extratropical Cyclone Activity:', self)
        Emeridional850 = QLabel(f"Path to meridional wind at 850 hPa data files for Extratropical Cyclone Activity:", self)
        Ezonal850 = QLabel(f"Path to zonal wind at 850 hPa data files for Extratropical Cyclone Activity:", self)

        self.Ez500T = QLineEdit(self)
        self.Ez500T.setText(self.pref)
        self.Ez500T.setCursorPosition(len(self.pref))

        self.Emeridional850T = QLineEdit(self)
        self.Emeridional850T.setText(self.pref)
        self.Emeridional850T.setCursorPosition(len(self.pref))

        self.Ezonal850T = QLineEdit(self)
        self.Ezonal850T.setText(self.pref)
        self.Ezonal850T.setCursorPosition(len(self.pref))
        
        #Extratropical cyclone activity obs data files 
        self.Ez500obs = QLabel(f'Path to Z500 observation data files for Extratropical Cyclone Activity:', self)
        self.Ez500Tobs = QLineEdit(self)
        self.Ez500Tobs.setText(self.prefix)
        self.Ez500Tobs.setCursorPosition(len(self.prefix))

        self.Emeridional850obs = QLabel(f'Path to meridional wind at 850 hPa observation data files for Extratropical Cyclone Activity:', self)
        self.Emeridional850Tobs = QLineEdit(self)
        self.Emeridional850Tobs.setText(self.prefix)
        self.Emeridional850Tobs.setCursorPosition(len(self.prefix))

        self.Ezonal850obs = QLabel(f'Path to zonal wind at 850 hPa observation data files for Extratropical Cyclone Activity:', self)
        self.Ezonal850Tobs = QLineEdit(self)
        self.Ezonal850Tobs.setText(self.prefix)
        self.Ezonal850Tobs.setCursorPosition(len(self.prefix))'''

        # Path to Z100 data files:
        z100 = QLabel(f'Path to Z100 model data files:', self)
        self.z100T = QLineEdit(self)
        self.z100T.setText(self.pref)
        self.z100T.setCursorPosition(len(self.pref))

            
        z100obs = QLabel(f'Path to Z100 observation data files:', self)
        self.z100Tobs = QLineEdit(self)
        self.z100Tobs.setText(self.prefix)
        self.z100Tobs.setCursorPosition(len(self.prefix))



        # Path to zonal wind at 850 hPa data files:
        zonalwind850 = QLabel(f'Path to zonal wind at 850 hPa model data files:', self)
        self.zonalwind850T = QLineEdit(self)
        self.zonalwind850T.setText(self.pref)
        self.zonalwind850T.setCursorPosition(len(self.pref))
        
            
        zonalwind850obs = QLabel(f'Path to zonal wind at 850 hPa observation data files:', self)
        self.zonalwind850Tobs = QLineEdit(self)
        self.zonalwind850Tobs.setText(self.prefix)
        self.zonalwind850Tobs.setCursorPosition(len(self.prefix))

        # Path to zonal wind at 200 hPa data files:
        
        zonalwind200 = QLabel(f'Path to zonal wind at 200 hPa model data files:', self)
        self.zonalwind200T = QLineEdit(self)
        self.zonalwind200T.setText(self.pref)
        self.zonalwind200T.setCursorPosition(len(self.pref))

            
        zonalwind200obs = QLabel(f'Path to zonal wind at 200 hPa observation data files:', self)
        self.zonalwind200Tobs = QLineEdit(self)
        self.zonalwind200Tobs.setText(self.prefix)
        self.zonalwind200Tobs.setCursorPosition(len(self.prefix))



        # Path to zonal wind at 10 hPa data files:
        zonalwind10 = QLabel(f'Path to zonal wind at 10 hPa model data files:', self)
        self.zonalwind10T = QLineEdit(self)
        self.zonalwind10T.setText(self.pref)
        self.zonalwind10T.setCursorPosition(len(self.pref))
   
        zonalwind10obs = QLabel(f'Path to zonal wind at 10 hPa observation data files:', self)
        self.zonalwind10Tobs = QLineEdit(self)
        self.zonalwind10Tobs.setText(self.prefix)
        self.zonalwind10Tobs.setCursorPosition(len(self.prefix))

        # Path to meridional wind at 850 hPa data files:
        meridionalwind850 = QLabel(f'Path to meridional wind at 850 hPa model data files:', self)
        self.meridionalwind850T = QLineEdit(self)
        self.meridionalwind850T.setText(self.pref)
        self.meridionalwind850T.setCursorPosition(len(self.pref))

                 
        meridionalwind850obs = QLabel(f'Path to meridional wind at 850 hPa observation data files:', self)
        self.meridionalwind850Tobs = QLineEdit(self)
        self.meridionalwind850Tobs.setText(self.prefix)
        self.meridionalwind850Tobs.setCursorPosition(len(self.prefix))

        # Path to meridional wind at 500 hPa data files:
        meridionalwind500 = QLabel(f'Path to meridional wind at 500 hPa model data files:', self)
        self.meridionalwind500T = QLineEdit(self)
        self.meridionalwind500T.setText(self.pref)
        self.meridionalwind500T.setCursorPosition(len(self.pref))

        meridionalwind500obs = QLabel(f'Path to meridional wind at 500 hPa observation data files:', self)
        self.meridionalwind500Tobs = QLineEdit(self)
        self.meridionalwind500Tobs.setText(self.prefix)
        self.meridionalwind500Tobs.setCursorPosition(len(self.prefix))

        # Path to temperature at 500 hPa data files:
        temperature500 = QLabel(f'Path to temperature at 500 hPa model data files:', self)
        self.temperature500T = QLineEdit(self)
        self.temperature500T.setText(self.pref)
        self.temperature500T.setCursorPosition(len(self.pref))
            
        temperature500obs = QLabel(f'Path to temperature at 500 hPa observation data files:', self)
        self.temperature500Tobs = QLineEdit(self)
        self.temperature500Tobs.setText(self.prefix)
        self.temperature500Tobs.setCursorPosition(len(self.prefix))

        #EKE
        #Are the model data daily-mean values? (Otherwise the data are instantaneous values)
        daily_mean_values_label = QLabel('Only for the Extratropical Cyclone Activity: Are the model data daily-mean values?', self)
        self.groupbox = QGroupBox()
        vbox = QVBoxLayout()
        self.groupbox.setLayout(vbox)
        self.daily_mean_values_yes = QRadioButton("Yes")
        self.daily_mean_values_yes.setChecked(True)
        vbox.addWidget(self.daily_mean_values_yes )
        self.daily_mean_values_no = QRadioButton("No")
        self.daily_mean_values_no.toggled.connect(self.clickedNo)
        vbox.addWidget(self.daily_mean_values_no)

        #If "No" in 1, what is the forecast time step interval in the model data?
        self.time_step_interval = QLabel('What is the forecast time step interval in the model data?', self)
        self.groupbox1 = QGroupBox()
        vbox2 = QVBoxLayout()
        self.groupbox1.setLayout(vbox2)
        self.time_step_interval_6 = QRadioButton("6")
        vbox2.addWidget(self.time_step_interval_6)
        
        self.time_step_interval_24 = QRadioButton("24")
        self.time_step_interval_24.setChecked(True)
        vbox2.addWidget(self.time_step_interval_24)
        

        diag_help_texts = ['']*13

        diag_help_texts[1] = '''
** STRIPES Index for geopotential height**        

Please include a trailing / in the directory where the geopotential data is located. Data can be 
geopotential (units m^2/s^2) or geopotential height. 
        '''
        diag_help_texts[2] = '''
        Help text for STRIPES Index for precipitation
'''
        diag_help_texts[3] = '''
        Help text for Pattern CC and Relative Amplitude over the PNA region
'''
        diag_help_texts[4] = '''
        Help text for Pattern CC and Relative Amplitude over the Euro-Atlantic sector
'''

        diag_help_texts[5] = '''
        Help text for Stratospheric pathway
'''
        diag_help_texts[6] = '''
        Help text for Histogram of 10 hPa zonal wind
'''
        diag_help_texts[7] = '''
** Extratropical Cyclone Activity**

- If model data contains ensembles, the input data for U850 and V850 must be provided for each ensemble member. Using the ensemble mean will result in eddy kinetic energy with underestimated amplitude.
- If model and verification data have different resolutions, it is highly recommended to provide the data on the same grid. Although this package has regridding capabilities it may take hours to days to complete the regridding especially for large ensembles. Usage of spherical harmonics is recommended for regridding of wind components. 

* Path to Extratropical Cyclone Activity Z500 model data files: Enter the name of Z500 files in the format <file_name_YYYYMMDDHH_exx.nc> where 'exx' denotes the ensemble members. E.g., for one ensemble member only: /project/$userid/z500_2011040100_e00.nc. For multiple ensemble members the count of ensemble members should also start from  '00', /project/$userid/z500_2011040100_e00.nc, /project/$userid/z500_2011040100_e01.nc'


* Path to Extratropical Cyclone Activity U850  model data files: Enter the name of U850 files in the format <file_name_YYYYMMDDHH_exx.nc> where 'exx' denotes the ensemble members.

* Path to Extratropical Cyclone Activity V850  model data files: Enter the name of V850 files in the format <file_name_YYYYMMDDHH_exx.nc> where 'exx' denotes the ensemble members.
'''
        diag_help_texts[8] = '''
        Help text for MJO
   
    
'''
        diag_help_texts[9] = '''
** Surface Air Temperature**

Please include a trailing / in the directory where the 2-meter temperature data is located



'''
       
        # Path to T2m data files:
        t2m = QLabel(f'Path to T2m model data files:', self)
        self.t2mT = QLineEdit(self)
        self.t2mT.setText(self.pref)
        self.t2mT.setCursorPosition(len(self.pref))

        t2mobs = QLabel(f'Path to T2m observation data files:', self)
        self.t2mTobs = QLineEdit(self)
        self.t2mTobs.setText(self.prefix)
        self.t2mTobs.setCursorPosition(len(self.prefix))

        # Path to precipitational data files:
        precData = QLabel(f'Path to precipitation model data files:', self)
        self.precDataT = QLineEdit(self)
        self.precDataT.setText(self.pref)
        self.precDataT.setCursorPosition(len(self.pref))

        precDataobs = QLabel(f'Path to precipitation observation data files:', self)
        self.precDataTobs = QLineEdit(self)
        self.precDataTobs.setText(self.prefix)
        self.precDataTobs.setCursorPosition(len(self.prefix))
            
        weeks = QLabel('Select weeks:', self)
        self.selectweeks = QLineEdit(self)

        #Compute the Z500 anomalies
        self.z500anomalies = QCheckBox("Compute the z500 anomalies")
        self.z500anomalies.setChecked(False)

        #self.dailyMean= QCheckBox("Are the model data daily-mean values?")
        #self.dailyMean.setChecked(False)

        but = QPushButton('Run', self)
        but.setFixedSize(70,30)
        but.clicked.connect(self.submi)
        
        showRes = QPushButton('Show results', self)
        showRes.setFixedSize(100,30)
        showRes.clicked.connect(self.showResults)
        helptext=''''''
        rendered=[]
        if(len(selected)>=1):
            if 1 in selected or 0 in selected: # stripes geopotential height
                #helptext+=diag_help_texts[1]+'\n\n'
                text = diag_help_texts[1]+'\n\n'
                lab=QLabel(text)
                lab.setWordWrap(True)
                left_layout.addWidget(lab)
                if 'z500T' not in rendered:
                    rendered.append('z500T')
                    right_layout.addWidget(z500)
                    right_layout.addWidget(self.z500T)
                    if era == False:
                        right_layout.addWidget(z500obs)
                        right_layout.addWidget(self.z500Tobs)
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Raised)
                separator.setLineWidth(3)
                right_layout.addWidget(separator)
            if 2 in selected or 0 in selected: #stripes index for precipitation
                #helptext+=diag_help_texts[2]+'\n\n'
                text = diag_help_texts[2]+'\n\n'
                lab=QLabel(text)
                lab.setWordWrap(True)
                left_layout.addWidget(lab)
                if 'precDataT' not in rendered:
                    rendered.append('precDataT')
                    right_layout.addWidget(precData)
                    right_layout.addWidget(self.precDataT)
                    if era == False:
                        right_layout.addWidget(precDataobs)
                        right_layout.addWidget(self.precDataTobs)
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Raised)
                separator.setLineWidth(3)
                right_layout.addWidget(separator)
            '''if 3 in selected or 11 in selected or 0 in selected: #Fraction of the observed STRIPES
                helptext+=diag_help_texts[3]+'\n\n'
                if 'z500T' not in rendered:
                    rendered.append('z500T')
                    for i in range(self.num_dates):
                        right_layout.addWidget(z500[i])
                        right_layout.addWidget(self.z500Ts[i])
                    if era == False:
                        right_layout.addWidget(z500obs)
                        right_layout.addWidget(self.z500Tobs)
                right_layout.addWidget(weeks)
                right_layout.addWidget(self.selectweeks)'''
            

            if 3 in selected or 0 in selected: #Pattern CC over & relative amplitude over PNA
                #helptext+=diag_help_texts[3]+'\n\n'
                text = diag_help_texts[3]+'\n\n'
                lab=QLabel(text)
                lab.setWordWrap(True)
                left_layout.addWidget(lab)
                if 'z500T' not in rendered:
                    rendered.append('z500T')
                    right_layout.addWidget(z500)
                    right_layout.addWidget(self.z500T)
                    if era == False:
                        right_layout.addWidget(z500obs)
                        right_layout.addWidget(self.z500Tobs)
                right_layout.addWidget(self.z500anomalies)
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Raised)
                separator.setLineWidth(3)
                right_layout.addWidget(separator)
                
        
            
            if 4 in selected or 0 in selected: #relative amplitude over PNA - NOW - pattern cc ...euro atlantic sector
                #helptext+=diag_help_texts[4]+'\n\n'
                text = diag_help_texts[4]+'\n\n'
                lab=QLabel(text)
                lab.setWordWrap(True)
                left_layout.addWidget(lab)
                if 'z500T' not in rendered:
                    rendered.append('z500T')
                    right_layout.addWidget(z500)
                    right_layout.addWidget(self.z500T)
                    if era == False:
                        right_layout.addWidget(z500obs)
                        right_layout.addWidget(self.z500Tobs)
                    separator = QFrame()
                    separator.setFrameShape(QFrame.HLine)
                    separator.setFrameShadow(QFrame.Raised)
                    separator.setLineWidth(3)
                    right_layout.addWidget(separator)
                
            if 5 in selected or 0 in selected: #Stratospheric pathway
                #helptext+=diag_help_texts[5]+'\n\n'
                text = diag_help_texts[5]+'\n\n'
                lab=QLabel(text)
                lab.setWordWrap(True)
                left_layout.addWidget(lab)
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
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Raised)
                separator.setLineWidth(3)
                right_layout.addWidget(separator)

            if 6 in selected or 0 in selected: #histogram of 10hpa zonal wind
                #helptext+=diag_help_texts[6]+'\n\n'
                text = diag_help_texts[6]+'\n\n'
                lab=QLabel(text)
                lab.setWordWrap(True)
                left_layout.addWidget(lab)
                if 'zonalwind10T' not in rendered:
                    rendered.append('zonalwind10T')
                    right_layout.addWidget(zonalwind10)
                    right_layout.addWidget(self.zonalwind10T)
                    if era == False:
                        right_layout.addWidget(zonalwind10obs)
                        right_layout.addWidget(self.zonalwind10Tobs)
                    separator = QFrame()
                    separator.setFrameShape(QFrame.HLine)
                    separator.setFrameShadow(QFrame.Raised)
                    separator.setLineWidth(3)
                    right_layout.addWidget(separator)
                        
            if 7 in selected or 0 in selected: #Extratropical cyclone activity
                #helptext+=diag_help_texts[7]+'\n\n'
                text = diag_help_texts[7]+'\n\n'
                lab=QLabel(text)
                lab.setWordWrap(True)
                left_layout.addWidget(lab)
                rendered.append('dailyMean')
                right_layout.addWidget(daily_mean_values_label)
                right_layout.addWidget(self.groupbox)
                self.daily_mean_ind = right_layout.count()-1
                
                if 'z500T' not in rendered:
                    rendered.append('z500T')
                    right_layout.addWidget(z500)
                    right_layout.addWidget(self.z500T)
                    if era == False:
                        right_layout.addWidget(z500obs)
                        right_layout.addWidget(self.z500Tobs)
                if 'meridionalwind850T' not in rendered:
                    rendered.append('meridionalwind850T')
                    right_layout.addWidget(meridionalwind850)
                    right_layout.addWidget(self.meridionalwind850T)
                    if era == False:
                        right_layout.addWidget(meridionalwind850obs)
                        right_layout.addWidget(self.meridionalwind850Tobs)
                
                if 'zonalwind850T' not in rendered:
                    rendered.append('zonalwind850T')
                    right_layout.addWidget(zonalwind850)
                    right_layout.addWidget(self.zonalwind850T)
                    if dict_file['RMM'] == False and era == False:
                        right_layout.addWidget(zonalwind850obs)
                        right_layout.addWidget(self.zonalwind850Tobs)
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Raised)
                separator.setLineWidth(3)
                right_layout.addWidget(separator)
                    
            if 8 in selected or 0 in selected: #MJO
                #helptext+=diag_help_texts[8]+'\n\n'
                text = diag_help_texts[8]+'\n\n'
                lab=QLabel(text)
                lab.setWordWrap(True)
                left_layout.addWidget(lab)
                rendered.append('dirOLR') #doesn't have a yaml entry
                right_layout.addWidget(dir_OLR_label)
                right_layout.addWidget(self.olrDataFiles)
                if dict_file['RMM'] == False and era == False:
                    right_layout.addWidget(dir_OLR_label_obs)
                    right_layout.addWidget(self.olrobsDataFiles)
                if 'zonalwind850T' not in rendered:
                    rendered.append('zonalwind850T')
                    right_layout.addWidget(zonalwind850)
                    right_layout.addWidget(self.zonalwind850T)
                    if dict_file['RMM'] == False and era == False:
                        right_layout.addWidget(zonalwind850obs)
                        right_layout.addWidget(self.zonalwind850Tobs) 
                if 'zonalwind200T' not in rendered:
                    rendered.append('zonalwind200T')
                    right_layout.addWidget(zonalwind200)
                    right_layout.addWidget(self.zonalwind200T)
                    if dict_file['RMM'] == False and era == False:
                        right_layout.addWidget(zonalwind200obs)
                        right_layout.addWidget(self.zonalwind200Tobs) 
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Raised)
                separator.setLineWidth(3)
                right_layout.addWidget(separator)
            if 9 in selected or 0 in selected: #T2m Surface Air Temp
                #helptext+=diag_help_texts[9]+'\n\n\n'
                text = diag_help_texts[9]+'\n\n'
                lab=QLabel(text)
                lab.setWordWrap(True)
                left_layout.addWidget(lab)
                rendered.append('t2mT')
                right_layout.addWidget(t2m)
                right_layout.addWidget(self.t2mT)
                if era == False:
                    right_layout.addWidget(t2mobs)
                    right_layout.addWidget(self.t2mTobs)
            
                

        self.right_layout = right_layout        
        self.selected=selected       
        self.right_layout.addStretch()
        #right_layout.addWidget(but,alignment=Qt.AlignRight)    

        back = QPushButton('Back', self)
        back.setFixedSize(70,30)
        back.clicked.connect(self.closee)

        help_label = QLabel(helptext)
        help_label.setWordWrap(True)
        
        
        #left_layout.addWidget(help_label)
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

        # Set the right layout to the stripesprecip widget of the splitter
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
        #central_layout.addWidget(showRes,1,5,alignment=Qt.AlignCenter)
        central_layout.addWidget(but,1,12,alignment=Qt.AlignRight)
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
            self.right_layout.insertWidget(self.daily_mean_ind+1,self.time_step_interval)
            self.right_layout.insertWidget(self.daily_mean_ind+2,self.groupbox1)
            self.right_layout.addStretch()
        else:
            self.right_layout.removeWidget(self.time_step_interval)
            self.time_step_interval.deleteLater()
            self.time_step_interval = None
            self.right_layout.removeWidget(self.groupbox1)
            self.groupbox1.deleteLater()
            self.groupbox1 = None
    
    def closee(self):
        self.close()
        self.parent.show()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.submi()
    def close_yaml(self):
        dict_file =self.dict_file
        dict_file['model data daily-mean values'] = self.daily_mean_values_yes.isChecked()
        if self.time_step_interval and self.time_step_interval_24.isChecked():
            dict_file['forecast time step']= 24
        else:
            dict_file['forecast time step']= 6

        #MJO's OLR data files
        dict_file['Path to OLR model data files']= self.olrDataFiles.text()
        if dict_file['RMM'] == False:
            dict_file['Path to OLR observation data files'] = self.olrobsDataFiles.text()
        
        
        #z500 model and its obs
        dict_file['Path to Z500 model data files'] = self.z500T.text()
        dict_file['Path to Z500 observation data files'] = self.z500Tobs.text()
        
        #z100 model and its obs
        dict_file['Path to z100 date files']= self.z100T.text()
        dict_file['Path to z100 observation files'] = self.z100Tobs.text()

        #zonalwind850 hpa model and obs
        dict_file['Path to zonal wind at 850 hPa model data files'] = self.zonalwind850T.text()
        if dict_file['RMM'] == False:
            dict_file['Path to zonal wind at 850 hPa observation data files'] = self.zonalwind850Tobs.text()
        
        #zonalwind200 hpa model and obs
        dict_file['Path to zonal wind at 200 hPa model data files'] = self.zonalwind200T.text()
        if dict_file['RMM'] == False:
            dict_file['Path to zonal wind at 200 hPa observation data files'] = self.zonalwind200Tobs.text()
        
        #zonalwind10 hpa model and obs
        dict_file['Path to zonal wind at 10 hPa model data files'] = self.zonalwind10T.text()
        dict_file['Path to zonal wind at 10 hPa observation data files'] = self.zonalwind10Tobs.text()


        '''#extratropical model files
        dict_file['Path to Extratropical Cyclone Activity Z500 model data files'] = self.Ez500T.text()
        dict_file['Path to meridional wind at 850 hPa data files for Extratropical Cyclone Activity'] = self.Emeridional850T.text()
        dict_file['Path to zonal wind at 850 hPa data files for Extratropical Cyclone Activity'] = self.Ezonal850T.text()
        
        #extratropical obs files
        dict_file['Extratropical Cyclone Activity Z500 observation data files'] = self.Ez500Tobs.text()
        dict_file['Extratropical Cyclone Activity meridional wind at 850 hPa observation data files'] = self.Emeridional850Tobs.text()
        dict_file['Extratropical Cyclone Activity zonal wind at 850 hPa observation data files'] = self.Ezonal850Tobs.text()'''
        
        #meridionalwind 850 hPa model and obs
        dict_file['Path to meridional wind at 850 hPa model data files']=self.meridionalwind850T.text()
        dict_file['Path to meridional wind at 850 hPa observation data files'] = self.meridionalwind850Tobs.text()
        
        #meridionalwind 500 hPa model and obs
        dict_file['Path to meridional wind at 500 hPa model data files'] = self.meridionalwind500T.text()
        dict_file['Path to meridional wind at 500 hPa observation data files'] = self.meridionalwind500Tobs.text()

        #Temperature at 500 hPa 
        dict_file['Path to temperature at 500 hPa model data files' ]=self.temperature500T.text()
        dict_file['Path to temperature at 500 hPa observation data files'] = self.temperature500Tobs.text()
    
        #Precipitational model and obs data files
        dict_file['Path to precipitation model data files'] = self.precDataT.text()
        dict_file['Path to precipitation observation data files'] = self.precDataTobs.text()
        
        #dict_file['Select weeks:'] = self.selectweeks.text()
        
        #t2m model and obs data
        dict_file['Path to T2m model data files for date'] = self.t2mT.text()
        dict_file['Path to T2m observation data files'] = self.t2mTobs.text()
        
        #z500 anomalies
        if self.z500anomalies.isChecked():
            dict_file['Compute the z500 anomalies'] = True
        else:
            dict_file['Compute the z500 anomalies'] = False

        dict_file['selected']=self.selected
        file = open(r'config.yml', 'w') 
        yaml.dump(dict_file, file)
        file.close()
        
        #run diagnostics
        diagnostics_path = ["../",
                            "../STRIPES/STRIPES_z500.py",
                            "../STRIPES/STRIPES_precip.py",
                            "../Pattern_CC_Amplitude/pna.py",
                            "../Pattern_CC_Amplitude/atlantic.py",
                            "../Stratosphere/stratosphere.py",
                            "../Histogram_10hPa/histogram.py",
                            "../eke/eke_plot.py", #extratropical cyclone activity
                            "../MJO/mjo.py",
                            "../T2m_composites/t2m_composites.py"]
        paths = 'python '+diagnostics_path[self.selected[0]]
        for i in self.selected[1:]:
            paths+=' & python '+diagnostics_path[i]
        return paths, dict_file
    
    def submi(self):
        slurm=self.showInputDialog()
        paths,dict_file = self.close_yaml()
        if slurm == -1:
            return
        if slurm == True:
            command=f"salloc  -p normal  -n 6  --cpus-per-task=12 --mem=24GB -t 0-02:00:00 bash -c 'source ../../miniconda/bin/activate; conda activate mjo_telecon;{paths}'"
            #self.ret = subprocess.Popen(command,  shell=True)
            
        elif slurm == False:
            command = paths
            
        dialog=LoadingDialog(self,command,self.selected,dict_file)  
            #self.ret.wait()
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.showResults()
        else:
            #display a window saying process is terminated
            QMessageBox.warning(self, "Process stopped", "Process execution terminated.")
      
    def showResults(self):
        QMessageBox.information(self, "Process Finished", "Process execution done!")
        self.nextwindow=FinalWindow(self,self.selected,self.dict_file)
        self.nextwindow.showMaximized()
        self.hide()
        
    def showInputDialog(self):
        dialog = InputDialog2()
        result = dialog.exec_()
        if dialog.result == True:
            return True
        elif dialog.result == False:
            return False
        else:
            return -1
    
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
                #print(f"Error running script {path}: {e}")

    # Wait for all subprocesses to complete
        for process in self.processes:
            process.wait()'''
        self.ret = subprocess.Popen(self.command, shell=True)
        self.ret.wait()
        #print('Execution done in Subprocess thread')

class InputDialog2(QDialog):
    def __init__(self):
        super().__init__()
        self.result=None
        self.initUI()

    def initUI(self):
        layout=QGridLayout()
        self.input_label = QLabel('Are you using SLURM to run resource-intensive jobs?')
        self.ok_button = QPushButton('Yes')
        self.cancel_button = QPushButton('No')
        self.ok_button.clicked.connect(self.yes_clicked)
        self.cancel_button.clicked.connect(self.no_clicked)
        layout.addWidget(self.input_label,0,0)
        layout.addWidget(self.ok_button,1,0,alignment=Qt.AlignLeft)
        layout.addWidget(self.cancel_button,1,12,alignment=Qt.AlignRight)
        self.setLayout(layout)
    def yes_clicked(self):
        self.result = True
        self.accept()
    def no_clicked(self):
        self.result = False
        self.accept()
        
class LoadingDialog(QDialog):
    def __init__(self, parent,command,selected,dict_file,):
        #super(LoadingDialog, self).__init__()
        super().__init__()
        self.selected=selected
        self.parent=parent
        self.dict_file=dict_file
        self.resize(400,200)
        self.subprocess_runner = SubprocessRunner(command)
        self.subprocess_runner.finished.connect(self.close)
        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.setLabelText("Running diagnostics...")
        self.progress_dialog.resize(400, 200)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setRange(0, 0)  # Set to an indeterminate progress bar
        self.progress_dialog.setWindowTitle("Please wait")
        self.progress_dialog.rejected.connect(self.close)
        self.subprocess_runner.start()
        
    def on_rejected(self):
        self.subprocess_runner.ret.terminate()
        self.subprocess_runner.ret.wait()
        self.subprocess_runner.terminate()  # Terminate the subprocess
        #print('terminated')
        self.subprocess_runner.wait()  # Wait for the subprocess to finish
        self.close()

    def closeEvent(self, event):
        if self.subprocess_runner.isRunning():
            #print('terminated')
            self.subprocess_runner.ret.terminate()
            self.subprocess_runner.ret.wait()
            self.close()
            #self.parent.show()
            event.accept()
        else:
            #print('About to close the loading page')
            super().accept()
            self.close()
            #self.parent.show()
            event.accept()


def get_all_files_in_directory(directory):
    #Check if the path is a directory
    abs_directory = os.path.abspath(directory)
    
    # Check if the path is a directory
    if not os.path.isdir(abs_directory):
        #print(f"{abs_directory} is not a valid directory.")
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
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.runn()
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
                self.model_name = dialog.input_text.text()#.lower()
                self.model_name,self.selected = get_model_diagnostics(self.model_name)
                if self.model_name:
                    self.dict_file['model name'] = self.model_name
                    #print(f"Accepted: {self.model_name}")
                    f=1
                    break  # Break the loop when valid input is provided
                else:
                    #print(self.model_name)
                    self.showErrorMessage("There is no model with this name.")
            else:
                #print("Canceled")
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
        help_label.setWordWrap(True)
        self.stripesgeopot = QRadioButton("STRIPES Index for geopotential height")
        self.stripesgeopot.setChecked(False) # 1

        self.stripesprecip = QRadioButton("STRIPES Index for precipitation")
        self.stripesprecip.setChecked(False) #2

        self.patterncc_pna = QRadioButton("Pattern CC and Relative Amplitude over the PNA region")
        self.patterncc_pna.setChecked(False) #3

        self.patterncc_atlantic = QRadioButton("Pattern CC and Relative Amplitude over the Euro-Atlantic sector")
        self.patterncc_atlantic.setChecked(False) #4

        #self.fourth = QRadioButton("Fraction of the observed STRIPES index for geopotential height")
        #self.fourth.setChecked(False) #4

        #self.fifth = QRadioButton("Relative amplitude over PNA?")
        #self.fifth.setChecked(False) #5

        self.strat_path = QRadioButton("Stratospheric pathway")
        self.strat_path.setChecked(False) #5

        self.zonal_wind_hist = QRadioButton("Histogram of 10 hPa zonal wind")
        self.zonal_wind_hist.setChecked(False) #6

        self.et_cyclone = QRadioButton("Extratropical cyclone activity")
        self.et_cyclone.setChecked(False) #7

        #self.nine = QRadioButton("EKE850-Z500 correlation")
        #self.nine.setChecked(False) #9

        self.mjo = QRadioButton("MJO")
        self.mjo.setChecked(False) #8

        self.t2m = QRadioButton("Surface air temperature")
        self.t2m.setChecked(False) #9

        
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
        
        
        if 0 in selected:
            right_layout.addWidget(self.stripesgeopot)
            right_layout.addWidget(self.stripesprecip)
            right_layout.addWidget(self.patterncc_pna)
            right_layout.addWidget(self.patterncc_atlantic)
            #right_layout.addWidget(self.fourth)
            #right_layout.addWidget(self.fifth)
            right_layout.addWidget(self.strat_path)
            right_layout.addWidget(self.zonal_wind_hist)
            right_layout.addWidget(self.et_cyclone)
            #right_layout.addWidget(self.nine)
            right_layout.addWidget(self.mjo)
            right_layout.addWidget(self.t2m)
        else:      
            if 1 in selected:
                right_layout.addWidget(self.stripesgeopot)

            if 2 in selected:
                right_layout.addWidget(self.stripesprecip)

            if 3 in selected:
                right_layout.addWidget(self.patterncc_pna)

            if 4 in selected:
                right_layout.addWidget(self.patterncc_atlantic)

            #if i==4:
             #   right_layout.addWidget(self.fourth)

            #if i==5:
             #   right_layout.addWidget(self.fifth)

            if 5 in selected:
                right_layout.addWidget(self.strat_path)

            if 6 in selected:
                right_layout.addWidget(self.zonal_wind_hist)

            if 7 in selected:
                right_layout.addWidget(self.et_cyclone)   
            #if i==9:
                #right_layout.addWidget(self.nine)    
            if 8 in selected:
                right_layout.addWidget(self.mjo)   
            if 9 in selected:
                right_layout.addWidget(self.t2m)
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

        # Set the right layout to the stripesprecip widget of the splitter
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
        f=0
        if self.stripesgeopot.isChecked():
            f=1
            self.win1 = firstResult(self,self.dict_file)
            self.win1.show()
        elif self.stripesprecip.isChecked():
            f=1
            self.win2 = stripesprecipResult(self,self.dict_file)
            self.win2.show()
        elif self.patterncc_pna.isChecked():
            f=1
            self.win2 = thirdResult(self,self.dict_file)
            self.win2.show()
        elif self.patterncc_atlantic.isChecked():
            f=1
            self.win2 = third2Result(self,self.dict_file)
            self.win2.show() #fourth
        #elif self.fifth.isChecked():
         #   f=1
          #  self.win2 = fifthResult(self,self.dict_file)
          
          #  self.win2.show() 
        
        elif self.strat_path.isChecked():
            f=1
            self.win2 = strat_pathResult(self,self.dict_file)
            self.win2.show()
        elif self.zonal_wind_hist.isChecked():
            f=1
            self.win2 = zonal_wind_histResult(self,self.dict_file)
            self.win2.show()
        elif self.et_cyclone.isChecked():
            f=1
            self.win2 = et_cycloneResult(self,self.dict_file)
            self.win2.show()
        elif self.mjo.isChecked():
            f=1
            self.win2 = mjoResult(self,self.dict_file)
            self.win2.show()
        elif self.t2m.isChecked():
            f=1
            self.win2 = t2mResult(self,self.dict_file)
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
        
class t2mResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        self.parent = parent
        self.model_name = dict_file['model name']
        self.setWindowTitle('Surface air temperature results')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)
        self.viewImages=[]
        #Create the weather image widget
        self.all_files=get_all_files_in_directory(f'../output/T2m/{self.model_name}')
        self.imagebuttons=[]
        self.helpTexts=['Helptext for image1','Helptext for image2','Helptext for image3','Helptext for image4','Helptext for image5','Helptext for image 6','Helptext for image 7','Helptext for image 8']
        for i in range(len(self.all_files)):
            buttonn=QPushButton(f'T2m Fig.{i+1}', self)
            buttonn.clicked.connect(self.openweek1_2(self.all_files[i],i,self.helpTexts[i]))
            self.viewImages.append(False)
            self.imagebuttons.append(buttonn)
        back = QPushButton('Back', self)
        back.clicked.connect(self.closee)
        back.setFixedSize(70,30)
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
        
        for i in range(len(self.all_files)//2):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)
        
        for i in range(len(self.all_files)//2,len(self.all_files)):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            ryt_layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)

        
    

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


    def openweek1_2(self, path,i,helpText):
        def clickk():
            #print(path,i)
            if self.viewImages[i] == False or self.viewImage.isVisible() == False:
                self.viewImage = viewImage(path,f'T2m Fig.{i}',helpText)
                self.viewImages[i] = self.viewImage
                #self.viewImage1.closed.connect(self.quit1)
                self.viewImages[i].show()
        return clickk
    def closee(self):
        self.close()
        self.parent.show()




class mjoResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        #self.setupUi(self)
        self.parent = parent
        self.setWindowTitle('MJO')
        self.model_name = dict_file['model name']
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)
        self.viewImages=[]
        #Create the weather image widget
        self.all_files=get_all_files_in_directory(f'../output/MJO/{self.model_name}')
        #print(len(self.all_files))
        self.imagebuttons=[]
        self.helpTexts=['''
        MJO index forecast skill: MJO prediction skill for UFS5, 6, 7, 8 reforecasts initialized with active MJO events during boreal winter (NDJFM). The prediction skill is evaluated based on the anomaly correlation coefficient (ACC, solid lines) and root-mean squared error (RMSE, dashed lines) between the model and observed RMM indices. The gray solid horizontal line indicates ACC of 0.5 and RMSE of 1.5.
        ''','''
        Longitude-time composite: Longitude-time composites of OLR (W/m2; shading) and U850 (contour; interval 0.3 m/s) anomalies averaged over 15S-15N for active MJO events. The vertical lines indicate 120E (approximately the center of the Maritime Continent), respectively. A 5-day moving average is applied.
        ''']
        for i in range(len(self.all_files)):
            buttonn=QPushButton(f'MJO Fig.{i+1}', self)
            buttonn.clicked.connect(self.openweek1_2(self.all_files[i],i,self.helpTexts[i]))
            
            self.viewImages.append(False)
            self.imagebuttons.append(buttonn)
            
       
        back = QPushButton('Back', self)
        back.clicked.connect(self.closee)
        back.setFixedSize(70,30)
        
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
        
        for i in range(len(self.all_files)//2):
            layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)
        
        for i in range(len(self.all_files)//2,len(self.all_files)):
            ryt_layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)

        
    

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


    def openweek1_2(self, path,i,helpText):
        def clickk():
            #print(path,i)
            if self.viewImages[i] == False or self.viewImage.isVisible() == False:
                self.viewImage = viewImage(path,f'MJO Fig.{i}',helpText)
                self.viewImages[i] = self.viewImage
                #self.viewImage1.closed.connect(self.quit1)
                self.viewImages[i].show()
        return clickk
    def closee(self):
        self.close()
        self.parent.show()

class et_cycloneResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        self.parent = parent
        self.model_name = dict_file['model name']
        self.setWindowTitle('Extratropical cyclone activity results')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)
        self.viewImages=[]
        self.all_files=get_all_files_in_directory(f'../output/ET_Cyclone/{self.model_name}')
        #print(len(self.all_files))
        self.imagebuttons=[]
        #self.helpTexts=['Helptext for image1','Helptext for image2','Helptext for image3','Helptext for image4','Helptext for image5','Helptext for image6','Helptext for image7','Helptext for image8','Helptext for image9',]
        self.helpTexts=[ '''
Extratropical cyclone activity (EKE850) composite in weeks 3-4 after the MJO in phases 2-3 for Reanalysis (left) and model reforecast (right). Dotted regions represent where the anomalies are statistically significant at the 0.05 level based on a bootstrap resampling calculation. Pattern correlation between model and Reanalysis over the northern hemisphere (20-80N) is shown in the upper right corner.
               ''','''
Extratropical cyclone activity (EKE850) composite in weeks 3-4 after the MJO in phases 4-5 for Reanalysis (left) and model reforecast (right). Dotted regions represent where the anomalies are statistically significant at the 0.05 level based on a bootstrap resampling calculation. Pattern correlation between model and Reanalysis over the northern hemisphere (20-80N) is shown in the upper right corner.
              ''','''
Extratropical cyclone activity (EKE850) composite in weeks 3-4 after the MJO in pahses 6-7 composite for Reanalysis (left) and model reforecast (right). Dotted regions represent where the anomalies are statistically significant at the 0.05 level based on a bootstrap resampling calculation. Pattern correlation between model and Reanalysis over the northern hemisphere (20-80N) is shown in the upper right corner.
             ''','''
Extratropical cyclone activity (EKE850) composite in weeks 3-4 after the MJO in pases 8-1 for Reanalysis (left) and model reforecast (right). Dotted regions represent where the anomalies are statistically significant at the 0.05 level based on a bootstrap resampling calculation. Pattern correlation between model and Reanalysis over the northern hemisphere (20-80N) is shown in the upper right corner.
            ''','''
Pattern correlation of week 3-4 composites of EKE850 (y-axis) and Z500 (x-axis) between Reanalysis and model reforecast over the North Atlantic (20-80N, 90W-30E), the North Pacific and North America (20-80N, 120E-90W), and the Northern Hemisphere (20-80N). The dots represent phases 8-1, 2-3, 4-5 and 6-7, respectively.
            ''','''
500-hPa geopotential height (Z500) composite in weeks 3-4 after the MJO phases 2-3 for Reanalysis (left) and model reforecast (right). Dotted regions represent where the anomalies are statistically significant at the 0.05 level based on a bootstrap resampling calculation. Pattern correlation between model and Reanalysis over the northern hemisphere (20-80N) is shown in the upper right corner.
            ''','''
500-hPa geopotential height (Z500) composite in weeks 3-4 after the MJO in phases 4-5 for Reanalysis (left) and model reforecast (right). Dotted regions represent where the anomalies are statistically significant at the 0.05 level based on a bootstrap resampling calculation. Pattern correlation between model and Reanalysis over the northern hemisphere (20-80N) is shown in the upper right corner.
            ''','''
500-hPa geopotential height (Z500) composite in weeks 3-4 after the MJO in phases 6-7 for Reanalysis (left) and model reforecast (right). Dotted regions represent where the anomalies are statistically significant at the 0.05 level based on a bootstrap resampling calculation. Pattern correlation between model and Reanalysis over the northern hemisphere (20-80N) is shown in the upper right corner.
            ''','''
500-hPa geopotential height (Z500) composite in weeks 3-4 after the MJO phases 8-1 for Reanalysis (left) and model reforecast (right). Dotted regions represent where the anomalies are statistically significant at the 0.05 level based on a bootstrap resampling calculation. Pattern correlation between model and Reanalysis over the northern hemisphere (20-80N) is shown in the upper right corner.
            ''']

        for i in range(len(self.all_files)):
            buttonn=QPushButton(f'ET-Cyclone Fig.{i+1}', self)
            buttonn.clicked.connect(self.openweek1_2(self.all_files[i],i,self.helpTexts[i]))
            
            self.viewImages.append(False)
            self.imagebuttons.append(buttonn)
            
       
        back = QPushButton('Back', self)
        back.clicked.connect(self.closee)
        back.setFixedSize(70,30)
        
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
        
        for i in range(len(self.all_files)//2):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)
        
        for i in range(len(self.all_files)//2,len(self.all_files)):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            ryt_layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)

        
    

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


    def openweek1_2(self, path,i,helpText):
        def clickk():
            #print(path,i)
            if self.viewImages[i] == False or self.viewImage.isVisible() == False:
                self.viewImage = viewImage(path,f'ET Cyclone Fig.{i}',helpText)
                self.viewImages[i] = self.viewImage
                #self.viewImage1.closed.connect(self.quit1)
                self.viewImages[i].show()
        return clickk
    def closee(self):
        self.close()
        self.parent.show()
class zonal_wind_histResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        self.parent = parent
        self.model_name = dict_file['model name']
        self.setWindowTitle('Histogram of 10 hPa zonal wind results')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)
        self.viewImages=[]
        #Create the weather image widget
        self.all_files=get_all_files_in_directory(f'../output/Zonal_Wind_Hist/{self.model_name}')
        #print(len(self.all_files))
        self.imagebuttons=[]
        self.helpTexts=['Helptext for image1','Helptext for image2','Helptext for image3','Helptext for image4']
        for i in range(len(self.all_files)):
            buttonn=QPushButton(f'Zonal wind hist Fig.{i+1}', self)
            buttonn.clicked.connect(self.openweek1_2(self.all_files[i],i,self.helpTexts[i]))
            
            self.viewImages.append(False)
            self.imagebuttons.append(buttonn)
            
       
        back = QPushButton('Back', self)
        back.clicked.connect(self.closee)
        back.setFixedSize(70,30)
        
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
        
        for i in range(len(self.all_files)//2):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)
        
        for i in range(len(self.all_files)//2,len(self.all_files)):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            ryt_layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)

        
    

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


    def openweek1_2(self, path,i,helpText):
        def clickk():
            #print(path,i)
            if self.viewImages[i] == False or self.viewImage.isVisible() == False:
                self.viewImage = viewImage(path,f'Zonal wind hist Fig.{i}',helpText)
                self.viewImages[i] = self.viewImage
                #self.viewImage1.closed.connect(self.quit1)
                self.viewImages[i].show()
        return clickk
    def closee(self):
        self.close()
        self.parent.show()

'''class fifthResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        self.parent = parent
        self.model_name = dict_file['model name']
        self.setWindowTitle('Relative amplitude over PNA results')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)
        self.viewImages=[]
        #Create the weather image widget
        self.all_files=get_all_files_in_directory(f'../output/T2m/{self.model_name}')
        #print(len(self.all_files))
        self.imagebuttons=[]
        for i in range(len(self.all_files)):
            buttonn=QPushButton(f'T2m Fig.{i+1}', self)
            buttonn.clicked.connect(self.openweek1_2(self.all_files[i],i))
            
            self.viewImages.append(False)
            self.imagebuttons.append(buttonn)
            
       
        back = QPushButton('Back', self)
        back.clicked.connect(self.closee)
        back.setFixedSize(70,30)
        
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
        
        for i in range(len(self.all_files)//2):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)
        
        for i in range(len(self.all_files)//2,len(self.all_files)):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            ryt_layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)

        
    

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


    def openweek1_2(self, path,i):
        def clickk():
            #print(path,i)
            if self.viewImages[i] == False or self.viewImage.isVisible() == False:
                self.viewImage = viewImage(path,f'T2m - {i}')
                self.viewImages[i] = self.viewImage
                #self.viewImage1.closed.connect(self.quit1)
                self.viewImages[i].show()
        return clickk
    def closee(self):
        self.close()
        self.parent.show()'''

class strat_pathResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        self.parent = parent
        self.model_name = dict_file['model name']
        self.setWindowTitle('Stratospheric pathway')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)
        self.viewImages=[]
        #Create the weather image widget
        self.all_files=get_all_files_in_directory(f'../output/Strat_Path/{self.model_name}')
        #print(len(self.all_files))
        self.imagebuttons=[]
        self.helpTexts=['Helptext for image1','Helptext for image2','Helptext for image3','Helptext for image4']
        for i in range(len(self.all_files)):
            buttonn=QPushButton(f'Strat Path Fig.{i+1}', self)
            buttonn.clicked.connect(self.openweek1_2(self.all_files[i],i,self.helpTexts[i]))
            
            self.viewImages.append(False)
            self.imagebuttons.append(buttonn)
            
       
        back = QPushButton('Back', self)
        back.clicked.connect(self.closee)
        back.setFixedSize(70,30)
        
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
        
        for i in range(len(self.all_files)//2):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)
        
        for i in range(len(self.all_files)//2,len(self.all_files)):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            ryt_layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)

        
    

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


    def openweek1_2(self, path,i,helpText):
        def clickk():
            #print(path,i)
            if self.viewImages[i] == False or self.viewImage.isVisible() == False:
                self.viewImage = viewImage(path,f'Strat Path Fig.{i}',helpText)
                self.viewImages[i] = self.viewImage
                #self.viewImage1.closed.connect(self.quit1)
                self.viewImages[i].show()
        return clickk
    def closee(self):
        self.close()
        self.parent.show()

    
class third2Result(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        self.parent = parent
        self.model_name = dict_file['model name']
        self.setWindowTitle('Pattern CC and Relative Amplitude over the Euro-Atlantic sector')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)
        self.viewImages=[]
        #Create the weather image widget
        self.all_files=get_all_files_in_directory(f'../output/PatternCC_Atlantic/{self.model_name}')
        #print(len(self.all_files))
        self.imagebuttons=[]
        self.helpTexts=['Helptext for image1','Helptext for image2','Helptext for image3','Helptext for image4']
        for i in range(len(self.all_files)):
            buttonn=QPushButton(f'Euro Atl sect Fig.{i+1}', self)
            buttonn.clicked.connect(self.openweek1_2(self.all_files[i],i,self.helpTexts[i]))
            
            self.viewImages.append(False)
            self.imagebuttons.append(buttonn)
            
       
        back = QPushButton('Back', self)
        back.clicked.connect(self.closee)
        back.setFixedSize(70,30)
        
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
        
        for i in range(len(self.all_files)//2):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)
        
        for i in range(len(self.all_files)//2,len(self.all_files)):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            ryt_layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)

        
    

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


    def openweek1_2(self, path,i,helpText):
        def clickk():
            #print(path,i)
            if self.viewImages[i] == False or self.viewImage.isVisible() == False:
                self.viewImage = viewImage(path,f'Euro Atl sect Fig.{i}',helpText)
                self.viewImages[i] = self.viewImage
                #self.viewImage1.closed.connect(self.quit1)
                self.viewImages[i].show()
        return clickk
    def closee(self):
        self.close()
        self.parent.show()

class fourthResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        self.parent = parent
        self.model_name = dict_file['model name']
        self.setWindowTitle('Fraction of the observed STRIPE Index for geopotential height results')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)
        self.viewImages=[]
        #Create the weather image widget
        self.all_files=get_all_files_in_directory(f'../output/T2m/{self.model_name}')
        #print(len(self.all_files))
        self.imagebuttons=[]
        self.helpTexts=['Helptext for image1','Helptext for image2','Helptext for image3','Helptext for image4']
        for i in range(len(self.all_files)):
            buttonn=QPushButton(f'T2m Fig.{i+1}', self)
            buttonn.clicked.connect(self.openweek1_2(self.all_files[i],i,self.helpTexts[i]))
            
            self.viewImages.append(False)
            self.imagebuttons.append(buttonn)
            
       
        back = QPushButton('Back', self)
        back.clicked.connect(self.closee)
        back.setFixedSize(70,30)
        
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
        
        for i in range(len(self.all_files)//2):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)
        
        for i in range(len(self.all_files)//2,len(self.all_files)):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            ryt_layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)

        
    

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


    def openweek1_2(self, path,i,helpText):
        def clickk():
            #print(path,i)
            if self.viewImages[i] == False or self.viewImage.isVisible() == False:
                self.viewImage = viewImage(path,f'T2m Fig.{i}',helpText)
                self.viewImages[i] = self.viewImage
                #self.viewImage1.closed.connect(self.quit1)
                self.viewImages[i].show()
        return clickk
    def closee(self):
        self.close()
        self.parent.show()


class firstResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        self.parent = parent
        self.model_name = dict_file['model name']
        self.setWindowTitle('STRIPES Index for geopotential height')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)
        self.viewImages=[]
        #Create the weather image widget
        self.all_files=get_all_files_in_directory(f'../output/StripesGeopot/{self.model_name}')
        #print(len(self.all_files))
        self.imagebuttons=[]
        self.helpTexts=['''
Geopotential height at 500 hPa: (top) STRIPES index (m) for observations. (middle) STRIPES index (m) for forecast. Larger values of the STRIPES index indicate higher amplitude co-variability of the 500 hPa geopotential height with the MJO. (bottom) Difference in the STRIPES index (m) between forecast and observations. Negative (positive) values of the difference indicate forecasts that have less (more) co-variability with the MJO than observed. 
            ''','''
Geopotential height at 500 hPa: (top) STRIPES index (m) for observations. (middle) STRIPES index (m) for forecast. Larger values of the STRIPES index indicate higher amplitude co-variability of the 500 hPa geopotential height with the MJO. (bottom) Difference in the STRIPES index (m) between forecast and observations. Negative (positive) values of the difference indicate forecasts that have less (more) co-variability with the MJO than observed. 
            ''','''
Geopotential height at 500 hPa: (top) STRIPES index (m) for observations. (middle) STRIPES index (m) for forecast. Larger values of the STRIPES index indicate higher amplitude co-variability of the 500 hPa geopotential height with the MJO. (bottom) Difference in the STRIPES index (m) between forecast and observations. Negative (positive) values of the difference indicate forecasts that have less (more) co-variability with the MJO than observed. 
           ''']
        for i in range(len(self.all_files)):
            buttonn=QPushButton(f'STRIPES Geopot Fig.{i+1}', self)
            buttonn.clicked.connect(self.openweek1_2(self.all_files[i],i,self.helpTexts[i]))
            self.viewImages.append(False)
            self.imagebuttons.append(buttonn)
            
       
        back = QPushButton('Back', self)
        back.clicked.connect(self.closee)
        back.setFixedSize(70,30)
        
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
        
        for i in range(len(self.all_files)//2):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)
        
        for i in range(len(self.all_files)//2,len(self.all_files)):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            ryt_layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)

        
    

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


    def openweek1_2(self, path,i,helpText):
        def clickk():
            #print(path,i)
            if self.viewImages[i] == False or self.viewImage.isVisible() == False:
                self.viewImage = viewImageStripes(path,f'STRIPES Geopot Fig.{i}',helpText)
                self.viewImages[i] = self.viewImage
                #self.viewImage1.closed.connect(self.quit1)
                self.viewImages[i].show()
        return clickk
    def closee(self):
        self.close()
        self.parent.show()
        
class stripesprecipResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        self.parent = parent
        self.model_name = dict_file['model name']
        self.setWindowTitle('STRIPES Index for precipitation')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)
        self.viewImages=[]
        #Create the weather image widget
        self.all_files=get_all_files_in_directory(f'../output/StripesPrecip/{self.model_name}')
        #print(len(self.all_files))
        self.imagebuttons=[]
        self.helpTexts=['''
Surface precipitation rate: (top) STRIPES index (mm) for observations. (middle) STRIPES index (mm) for forecast. Larger values of the STRIPES index indicate higher amplitude co-variability of the surface precipitation rate with the MJO. (bottom) Difference in the STRIPES index (mm) between forecast and observations. Negative (positive) values of the difference indicate forecasts that have less (more) co-variability with the MJO than observed. 
        ''','''
Surface precipitation rate: (top) STRIPES index (mm) for observations. (middle) STRIPES index (mm) for forecast. Larger values of the STRIPES index indicate higher amplitude co-variability of the surface precipitation rate with the MJO. (bottom) Difference in the STRIPES index (mm) between forecast and observations. Negative (positive) values of the difference indicate forecasts that have less (more) co-variability with the MJO than observed. 
        ''','''
Surface precipitation rate: (top) STRIPES index (mm) for observations. (middle) STRIPES index (mm) for forecast. Larger values of the STRIPES index indicate higher amplitude co-variability of the surface precipitation rate with the MJO. (bottom) Difference in the STRIPES index (mm) between forecast and observations. Negative (positive) values of the difference indicate forecasts that have less (more) co-variability with the MJO than observed. 
        ''']
        for i in range(len(self.all_files)):
            buttonn=QPushButton(f'STRIPES Precip Fig.{i+1}', self)
            buttonn.clicked.connect(self.openweek1_2(self.all_files[i],i,self.helpTexts[i]))
            
            self.viewImages.append(False)
            self.imagebuttons.append(buttonn)
            
       
        back = QPushButton('Back', self)
        back.clicked.connect(self.closee)
        back.setFixedSize(70,30)
        
        #Create a layout for the left half (weather image)
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
        
        for i in range(len(self.all_files)//2):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)
        
        for i in range(len(self.all_files)//2,len(self.all_files)):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            ryt_layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)

        
    

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


    def openweek1_2(self, path,i,helpText):
        def clickk():
            #print(path,i)
            if self.viewImages[i] == False or self.viewImage.isVisible() == False:
                self.viewImage = viewImageStripes(path,f'STRIPES Precip Fig.{i}',helpText)
                self.viewImages[i] = self.viewImage
                #self.viewImage1.closed.connect(self.quit1)
                self.viewImages[i].show()
        return clickk
    def closee(self):
        self.close()
        self.parent.show()

class thirdResult(QMainWindow):
    def __init__(self,parent,dict_file):
        super().__init__()
        self.parent = parent
        self.model_name = dict_file['model name']
        self.setWindowTitle('Pattern CC and Relative Amplitude over the PNA region')
        self.setGeometry(200, 200, 400, 200)  # Set window position and size
        #self.setMaximumSize(width, height)
        self.viewImages=[]
        #Create the weather image widget
        self.all_files=get_all_files_in_directory(f'../output/PatternCC_PNA/{self.model_name}')
        #print(len(self.all_files))
        self.imagebuttons=[]
        self.helpTexts=['Helptext for image1','Helptext for image2','Helptext for image3','Helptext for image4']
        for i in range(len(self.all_files)):
            buttonn=QPushButton(f'PatternCC_PNA Fig.{i+1}', self)
            buttonn.clicked.connect(self.openweek1_2(self.all_files[i],i,self.helpTexts[i]))
            
            self.viewImages.append(False)
            self.imagebuttons.append(buttonn)
            
       
        back = QPushButton('Back', self)
        back.clicked.connect(self.closee)
        back.setFixedSize(70,30)
        
        #Create a layout for the left half 
        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
        
        for i in range(len(self.all_files)//2):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)
        
        for i in range(len(self.all_files)//2,len(self.all_files)):
            ##print(self.imagebuttons[i])
            #self.imagebuttons[i].clicked.connect(lambda: self.openweek1_2(self.all_files[i],i))
            ryt_layout.addWidget(self.imagebuttons[i],alignment=Qt.AlignCenter)

        
    

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


    def openweek1_2(self, path,i,helpText):
        def clickk():
            #print(path,i)
            if self.viewImages[i] == False or self.viewImage.isVisible() == False:
                self.viewImage = viewImage(path,f'PatternCC_PNA Fig.{i}',helpText)
                self.viewImages[i] = self.viewImage
                #self.viewImage1.closed.connect(self.quit1)
                self.viewImages[i].show()
        return clickk
    def closee(self):
        self.close()
        self.parent.show()

class viewImage(QMainWindow):
    def __init__(self,imageP,title,helpText):
        super().__init__()
        imageP = os.path.abspath(imageP)
        self.setWindowTitle(title)
        self.setGeometry(200, 0, 850, 500)  # Set window position and size
        self.closed = pyqtSignal()
        #scroll_bar = QScrollBar(self)
        self.scroll = QScrollArea()
        image = QLabel(self)
        pixmap = QPixmap(imageP) 
        pixmap= pixmap.scaled(800, 600,Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image.setPixmap(pixmap)
        image.setAlignment(Qt.AlignCenter)
        self.imagep = imageP
        
        helpText = QLabel(helpText)
        helpText.setWordWrap(True)

        download = QPushButton('Download image', self)
        download.setFixedSize(300,30)
        download.clicked.connect(self.download_image)

        layout = QVBoxLayout()
        layout.addWidget(image)
        layout.addWidget(helpText,alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(download,alignment=Qt.AlignCenter)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        
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


class viewImageStripes(QMainWindow):
    def __init__(self,imageP,title,helpText):
        super().__init__()
        imageP = os.path.abspath(imageP)
        self.setWindowTitle(title)
        self.setGeometry(200, 0, 850, 500)  # Set window position and size
        self.closed = pyqtSignal()
        #scroll_bar = QScrollBar(self)
        self.scroll = QScrollArea()
        #Create the weather image widget
        image = QLabel(self)
        pixmap = QPixmap(imageP) 
        pixmap= pixmap.scaled(800, 600,Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image.setPixmap(pixmap)
        image.setAlignment(Qt.AlignCenter)
        self.imagep = imageP
        
        helpText = QLabel(helpText)
        helpText.setWordWrap(True)

        download = QPushButton('Download image', self)
        download.setFixedSize(300,30)
        download.clicked.connect(self.download_image)

        layout = QVBoxLayout()
        ryt_layout = QVBoxLayout()
        
        layout.addWidget(image)
        ryt_layout.addStretch()
        ryt_layout.addWidget(helpText,alignment=Qt.AlignCenter)
        ryt_layout.addStretch()
        ryt_layout.addWidget(download,alignment=Qt.AlignCenter)
        frame = QFrame()
        frame.setLayout(layout)
        ryt_frame = QFrame()
        ryt_frame.setLayout(ryt_layout)
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
        
        # Create a central widget to hold the splitter
        central_widget = QWidget()
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
        # #printing the checked status
        if checked:
            self.all.setChecked(True)
            self.stripesgeopot.setChecked(True)
            self.stripesprecip.setChecked(True)
            self.patterncc_pna.setChecked(True)
            self.patterncc_atlantic.setChecked(True)
            #self.fourth.setChecked(True)
            #self.fifth.setChecked(True)
            self.strat_path.setChecked(True)
            self.zonal_wind_hist.setChecked(True)
            self.et_cyclone.setChecked(True)
            #self.nine.setChecked(True)
            self.mjo.setChecked(True)
            self.t2m.setChecked(True)
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
        
       

        QLabel#round_count_label, QLabel#highscore_count_label{
            border: 1px solid #fff;
            border-radius: 8px;
            padding: 2px;
            font-size: 10pt;
        }
        QPushButton
        {
            color: black;
            background: #0577a8;
            border: 1px #DADADA solid;
            padding: 5px 10px;
            border-radius: 2px;
            font-weight: bold;
            outline: none;
        }
        
        
        QPushButton:hover{
            border: 1px #C6C6C6 solid;
            color: #fff;
            background: #0892D0;
        }
        QLineEdit {
            padding: 1px;
            color: black;
            border-style: solid;
            border: 2px solid #fff;
            border-radius: 8px;
        }

    """
     
    app.setStyleSheet(style)
    entry_window = StartWindow()
    entry_window.show()
    sys.exit(app.exec())

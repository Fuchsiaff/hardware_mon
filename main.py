from PyQt5 import QtTest
import subprocess
from PyQt5.QtWidgets import QWidget, QProgressBar, QApplication, QLabel, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QPoint, QProcess
import sys
import psutil
import time
import os


class Window(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(
            Qt.Widget |
            Qt.WindowCloseButtonHint |
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint
        )
        
        self.setParent(None)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.threading = ThreadClass()
        self.m_nMouseClick_X_Coordinate = None
        self.m_nMouseClick_Y_Coordinate = None
        self.st = os.statvfs("/")
        self.free = self.st.f_bavail * self.st.f_frsize
        self.total = self.st.f_blocks * self.st.f_frsize
        self.used = (self.st.f_blocks - self.st.f_bfree) * self.st.f_frsize
        self.usage = round(self.used/self.total*100)
        self.threading2 = ThreadClass2()
        self.threading3 = Temperature_thread()
        self.threading4 = Disk_thread()
        self.threading5 = Battery_watt_thread()
        self.threading3.start()
        self.threading2.start()
        self.threading.start()
        self.threading4.start()
        self.threading5.start()
        self.progress_stylesheet = """
        
        QProgressBar {
        border: 2px solid transparent;
        
        background-color: transparent;
        font-weight: bold;
        font-size: 13px;
        margin-left: -6px;
        }

        QProgressBar::chunk {
        background-color: #00ff00;
        width: 29px;
        
        }
        
        """
        
        self.temp_stylesheet = """
        
        QProgressBar {
        border: 2px solid transparent;
        
        background-color: transparent;
        font-weight: bold;
        font-size: 13px;
        margin-left: -6px;
        }

        QProgressBar::chunk {
        background-color: #00ff00;
        
        }
        
        """
        
        self.oldPos = self.pos()
        self.threading2.signal2.connect(self.ram_val)
        self.threading.signal.connect(self.cpu_val)
        self.threading3.signal3.connect(self.cpu_temp_val)
        self.threading4.signal4.connect(self.disk_usage_val)
        self.threading5.signal5.connect(self.battery_watt_val)

        self.initUI()


    def initUI(self):
        
        self.ram = QProgressBar(self)
        self.ram.setFixedWidth(150)
        self.ram.setValue(100)
        
        self.cpu = QProgressBar(self)
        self.cpu.setFixedWidth(150)
        self.cpu.setValue(100)
        
        self.cpu_temp = QProgressBar(self)
        self.cpu_temp.setFixedWidth(150)
        self.cpu_temp.setValue(100)
        self.cpu_temp.setFormat("%p°C")
        
        self.disk_usage = QProgressBar(self)
        self.disk_usage.setFixedWidth(150)
        self.disk_usage.setValue(self.usage)
        
        self.main_layout = QHBoxLayout()
        self.text_layout = QVBoxLayout()
        self.value_layout = QVBoxLayout()
        
        self.ram_text = QLabel("<h3>RAM USAGE:</h3> ", self)
        self.ram_text.setStyleSheet("color: #00ff00")
        
        self.cpu_value_text = QLabel("<h3>CPU TEMP:</h3> ", self)
        self.cpu_value_text.setStyleSheet("color: #00ff00") 
               
        self.cpu_text = QLabel("<h3>CPU USAGE:</h3> ", self)
        self.cpu_text.setStyleSheet("color: #00ff00")
        
        self.disk_usage_text = QLabel("<h3>DISK USED: </h3> ", self)
        self.disk_usage_text.setStyleSheet("color: #00ff00")
        
        self.disk_space_left_text = QLabel("<h3>FREE DISK SPACE:</h3> ")
        self.disk_space_left_text.setStyleSheet("color: #00ff00")
        self.disk_space_left_text.setAlignment(Qt.AlignBottom)
        
        self.disk_space_left = QLabel("<h3>" + str(int(self.free/1000000000)) + " GiB</h3>", self)
        self.disk_space_left.setStyleSheet("color: #000000; background-color: #00ff00")
        self.disk_space_left.setAlignment(Qt.AlignCenter)
        self.disk_space_left.setFixedWidth(70)
        self.disk_space_left.setFixedHeight(24)
        
        self.battery_usage_text = QLabel("<h3>POWER USAGE:</h3> ", self)
        self.battery_usage = QLabel("<h3>NaN</h3>", self)
        
        self.battery_usage_text.setStyleSheet("color: #00ff00")
        self.battery_usage.setStyleSheet("color: #000000; background-color: #00ff00")
        
        self.battery_usage.setAlignment(Qt.AlignCenter)
        self.battery_usage_text.setAlignment(Qt.AlignBottom)
        self.battery_usage.setFixedWidth(60)
        self.battery_usage.setFixedHeight(24)
        
        self.text_layout.addWidget(self.cpu_text)
        self.value_layout.addWidget(self.cpu)
        
        self.text_layout.addWidget(self.ram_text)
        self.value_layout.addWidget(self.ram)
        
        self.text_layout.addWidget(self.cpu_value_text)
        self.value_layout.addWidget(self.cpu_temp)
        
        self.text_layout.addWidget(self.disk_usage_text)
        self.value_layout.addWidget(self.disk_usage)
        
        self.text_layout.addWidget(self.disk_space_left_text)
        self.value_layout.addWidget(self.disk_space_left)
        
        self.text_layout.addWidget(self.battery_usage_text)
        self.value_layout.addWidget(self.battery_usage)
        
        self.main_layout.addLayout(self.text_layout)
        self.main_layout.addLayout(self.value_layout)
        
        self.cpu.setStyleSheet(self.progress_stylesheet)
        self.ram.setStyleSheet(self.progress_stylesheet)
        self.disk_usage.setStyleSheet(self.progress_stylesheet)
        self.cpu_temp.setStyleSheet(self.temp_stylesheet)
        self
        self.setLayout(self.main_layout)
        self.show()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
    
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
    
    def ram_val(self, ram_value):
        self.ram.setValue(ram_value)

    def cpu_val(self, cpu_value):
        self.cpu.setValue(cpu_value)
        
    def cpu_temp_val(self, temp_value):
        self.cpu_temp.setValue(temp_value)
        
    def disk_usage_val(self, value_tuple):
        free = value_tuple[0]  
        total = value_tuple[1]
        used = value_tuple[2]
        total_in_GiB = total/1000000000
        disk_used = round(used/total*100)
        self.disk_usage.setValue(int(disk_used))
        self.disk_space_left.setText("<h3>" + str(int(free/1000000000)) + " GiB</h3>")
        
    def battery_watt_val(self, battery_watt_value):
        self.battery_usage.setText("<h3>" + str(battery_watt_value) + " W</h3>")    


class ThreadClass(QThread):
    signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            value = psutil.cpu_percent(interval=1, percpu=True)
            cpu_value = sum(value) / len(value)
            self.signal.emit(cpu_value)
            time.sleep(0.3)


class ThreadClass2(QThread):
    signal2 = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            r_value = psutil.virtual_memory()
            ram_value = r_value[2]

            self.signal2.emit(ram_value)
            time.sleep(0.3)


class Temperature_thread(QThread):
    signal3 = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        
    def run(self):
        self.process = QProcess()
        
        while True:
            self.process.start("cat /sys/class/thermal/thermal_zone0/temp")
            self.process.waitForFinished(-1)
            temp_value = int(self.process.readAllStandardOutput())/1000
            self.signal3.emit(temp_value)
            time.sleep(0.3)
            
            
class Disk_thread(QThread):
    signal4 = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        
    def run(self):
        while True:
            st = os.statvfs("/")
            free = st.f_bavail * st.f_frsize
            total = st.f_blocks * st.f_frsize
            used = (st.f_blocks - st.f_bfree) * st.f_frsize
            self.signal4.emit((free, total, used))  
            time.sleep(30)   
            

class Battery_watt_thread(QThread):
    signal5 = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        
    def run(self):
        self.process = QProcess()
        while True:
            self.process.start("cat /sys/class/power_supply/BAT0/power_now")
            self.process.waitForFinished(-1)
            power_usage = int(self.process.readAllStandardOutput())/1000000
            self.signal5.emit(power_usage)
            time.sleep(0.3)
            
                        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = Window()
    sys.exit(app.exec_())
    

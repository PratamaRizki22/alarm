import sys
import os
import math
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox, 
                             QDateEdit, QTimeEdit, QHBoxLayout, QFileDialog)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QIcon
from PyQt5.QtCore import QDateTime, QTimer, QTime, Qt
import pygame
from threading import Thread

pygame.mixer.init()

class ClockWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 300)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        self.update()

    def paintEvent(self, event):
        current_time = QTime.currentTime()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        painter.translate(rect.center())
        painter.scale(rect.width() / 200.0, rect.height() / 200.0)
        
        painter.setBrush(QColor(30, 30, 30))
        painter.drawEllipse(-100, -100, 200, 200)
        
        font = QFont('Arial', 14, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        for i in range(1, 13):
            angle = 30 * i
            radian = math.radians(angle)
            x = 80 * math.cos(radian - math.pi / 2)
            y = 80 * math.sin(radian - math.pi / 2)
            painter.drawText(int(x - 10), int(y + 10), str(i))
        
        painter.save()
        hour_angle = 30 * (current_time.hour() % 12 + current_time.minute() / 60.0)
        painter.rotate(hour_angle)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(-5, -40, 10, 60)
        painter.restore()

        painter.save()
        minute_angle = 6 * (current_time.minute() + current_time.second() / 60.0)
        painter.rotate(minute_angle)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(-3, -70, 6, 90)
        painter.restore()

        painter.save()
        second_angle = 6 * current_time.second()
        painter.rotate(second_angle)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawRect(-1, -80, 2, 90)
        painter.restore()

class AlarmApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Alarm Desktop')
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")

        self.alarms = []
        self.alarm_sound_path = None

        main_layout = QVBoxLayout()

        self.clock_widget = ClockWidget()
        main_layout.addWidget(self.clock_widget)

        datetime_layout = QHBoxLayout()
        datetime_label = QLabel('Set Date and Time:')
        datetime_label.setFont(QFont('Arial', 12, QFont.Bold))
        datetime_layout.addWidget(datetime_label)

        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("font-size: 12pt; background-color: #3a3a3a; color: #ffffff; border: 1px solid #ffffff;")
        datetime_layout.addWidget(self.date_edit)

        self.time_edit = QTimeEdit(self)
        self.time_edit.setDisplayFormat('HH:mm:ss')
        self.time_edit.setStyleSheet("font-size: 12pt; background-color: #3a3a3a; color: #ffffff; border: 1px solid #ffffff;")
        datetime_layout.addWidget(self.time_edit)

        main_layout.addLayout(datetime_layout)

        self.set_alarm_button = QPushButton('Set Alarm', self)
        self.set_alarm_button.setIcon(QIcon('alarm_icon.png')) 
        self.set_alarm_button.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                font-weight: bold;
                color: white;
                background-color: #4CAF50;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.set_alarm_button.clicked.connect(self.set_alarm)
        main_layout.addWidget(self.set_alarm_button)

        self.choose_song_button = QPushButton('Choose Alarm Sound', self)
        self.choose_song_button.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                font-weight: bold;
                color: white;
                background-color: #2196F3;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.choose_song_button.clicked.connect(self.choose_alarm_sound)
        main_layout.addWidget(self.choose_song_button)

        self.setLayout(main_layout)

        self.alarm_timer = QTimer(self)
        self.alarm_timer.timeout.connect(self.check_alarms)
        self.alarm_timer.start(1000)  # Check every second

    def choose_alarm_sound(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose Alarm Sound", "", "Audio Files (*.mp3 *.wav);;All Files (*)", options=options)
        if file_name:
            self.alarm_sound_path = file_name
            QMessageBox.information(self, 'Alarm Sound', f'Alarm sound set to: {file_name}')

    def set_alarm(self):
        if not self.alarm_sound_path:
            QMessageBox.warning(self, 'No Alarm Sound', 'Please choose an alarm sound before setting an alarm.')
            return

        alarm_datetime = QDateTime(self.date_edit.date(), self.time_edit.time())
        self.alarms.append(alarm_datetime)
        QMessageBox.information(self, 'Alarm Set', f'Alarm set for {alarm_datetime.toString("yyyy-MM-dd HH:mm:ss")}')

    def check_alarms(self):
        current_datetime = QDateTime.currentDateTime()
        for alarm in self.alarms:
            if current_datetime >= alarm:
                try:
                    if self.alarm_sound_path and os.path.exists(self.alarm_sound_path):
                        pygame.mixer.music.load(self.alarm_sound_path)
                        pygame.mixer.music.play()
                    else:
                        QMessageBox.warning(self, 'Error', f'Alarm sound file not found: {self.alarm_sound_path}')
                except pygame.error as e:
                    QMessageBox.warning(self, 'Error', f'Failed to play alarm sound: {e}')
                self.alarms.remove(alarm)  

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AlarmApp()
    ex.show()
    sys.exit(app.exec_())

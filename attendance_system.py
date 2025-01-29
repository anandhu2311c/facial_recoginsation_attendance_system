import sys
import cv2
import json
import face_recognition
import numpy as np
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QStackedWidget, QTableWidget, QTableWidgetItem,
                             QDialog, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap


class FaceRegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New Face")
        self.setModal(True)
        self.setGeometry(200, 200, 640, 580)
        
        layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter name")
        layout.addWidget(self.name_input)
        
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(640, 480)
        layout.addWidget(self.camera_label)
        
        self.capture_button = QPushButton("Capture Face")
        self.capture_button.clicked.connect(self.capture_face)
        layout.addWidget(self.capture_button)
        
        self.setLayout(layout)
        
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)
        
        self.captured_encoding = None

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            face_locations = face_recognition.face_locations(frame)
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

    def capture_face(self):
        ret, frame = self.cap.read()
        if ret:
            face_locations = face_recognition.face_locations(frame)
            if not face_locations:
                QMessageBox.warning(self, "Error", "No face detected!")
                return
            
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            if face_encodings:
                self.captured_encoding = face_encodings[0]
                QMessageBox.information(self, "Success", "Face captured successfully!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to encode face!")

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        super().closeEvent(event)


class AttendanceSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Facial Recognition Attendance System")
        self.setGeometry(100, 100, 1200, 800)
        
        self.known_face_encodings = []
        self.known_face_names = []
        self.camera_active = False
        self.load_registered_faces()
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.init_recognition_screen()
        self.init_admin_login_screen()
        self.init_dashboard_screen()
        
        self.stacked_widget.setCurrentIndex(0)

    def init_recognition_screen(self):
        recognition_widget = QWidget()
        layout = QVBoxLayout()
        
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(640, 480)
        layout.addWidget(self.camera_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        controls_layout = QHBoxLayout()
        self.camera_button = QPushButton("Start Camera")
        self.camera_button.clicked.connect(self.toggle_camera)
        self.admin_button = QPushButton("Admin Login")
        self.admin_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        controls_layout.addWidget(self.camera_button)
        controls_layout.addWidget(self.admin_button)
        layout.addLayout(controls_layout)
        
        self.status_label = QLabel("System Ready")
        self.time_label = QLabel()
        layout.addWidget(self.status_label)
        layout.addWidget(self.time_label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        recognition_widget.setLayout(layout)
        self.stacked_widget.addWidget(recognition_widget)
        
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_camera)

    def init_admin_login_screen(self):
        login_widget = QWidget()
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        
        back_button = QPushButton("Back")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        self.login_status = QLabel("")
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        layout.addWidget(back_button)
        layout.addWidget(self.login_status)
        
        login_widget.setLayout(layout)
        self.stacked_widget.addWidget(login_widget)

    def init_dashboard_screen(self):
        dashboard_widget = QWidget()
        layout = QVBoxLayout()
        
        stats_layout = QHBoxLayout()
        self.total_students_label = QLabel("Total Students: 0")
        self.present_today_label = QLabel("Present Today: 0")
        stats_layout.addWidget(self.total_students_label)
        stats_layout.addWidget(self.present_today_label)
        layout.addLayout(stats_layout)
        
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(2)  # Removed "Time Out" column
        self.attendance_table.setHorizontalHeaderLabels(["Name", "Date"])
        layout.addWidget(self.attendance_table)
        
        register_button = QPushButton("Register New Face")
        register_button.clicked.connect(self.register_new_face)
        layout.addWidget(register_button)
        
        delete_face_button = QPushButton("Delete Registered Face")
        delete_face_button.clicked.connect(self.delete_registered_face)
        layout.addWidget(delete_face_button)
        
        delete_day_button = QPushButton("Delete Records for a Specific Day")
        delete_day_button.clicked.connect(self.delete_records_for_day)
        layout.addWidget(delete_day_button)
        
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(logout_button)
        
        dashboard_widget.setLayout(layout)
        self.stacked_widget.addWidget(dashboard_widget)

    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)

    def toggle_camera(self):
        if not self.camera_active:
            self.cap = cv2.VideoCapture(0)
            self.camera_timer.start(30)
            self.camera_button.setText("Stop Camera")
            self.camera_active = True
        else:
            self.camera_timer.stop()
            self.cap.release()
            self.camera_button.setText("Start Camera")
            self.camera_active = False

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                    self.record_attendance(name)
                
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
            
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if username == "admin" and password == "admin123":
            self.stacked_widget.setCurrentIndex(2)
            self.update_dashboard()
            self.login_status.setText("")
            self.username_input.clear()
            self.password_input.clear()
        else:
            self.login_status.setText("Invalid credentials")

    def register_new_face(self):
        dialog = FaceRegistrationDialog(self)
        if dialog.exec():
            name = dialog.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Please enter a name!")
                return
            
            if dialog.captured_encoding is not None:
                try:
                    with open("registered_faces.json", "r") as f:
                        data = json.load(f)
                        encodings = data.get("encodings", [])
                        names = data.get("names", [])
                except (FileNotFoundError, json.JSONDecodeError):
                    encodings = []
                    names = []
                
                encodings.append(dialog.captured_encoding.tolist())
                names.append(name)
                
                with open("registered_faces.json", "w") as f:
                    json.dump({"encodings": encodings, "names": names}, f)
                
                self.known_face_encodings = np.array(encodings)
                self.known_face_names = names
                
                QMessageBox.information(self, "Success", f"Successfully registered {name}!")
                self.update_dashboard()
            else:
                QMessageBox.warning(self, "Error", "No face was captured!")

    def delete_registered_face(self):
        name, ok = QInputDialog.getItem(self, "Delete Registered Face", "Select face to delete:", self.known_face_names, 0, False)
        
        if ok and name:
            index = self.known_face_names.index(name)
            self.known_face_names.pop(index)
            self.known_face_encodings = np.delete(self.known_face_encodings, index, axis=0)
            
            with open("registered_faces.json", "w") as f:
                json.dump({"encodings": self.known_face_encodings.tolist(), "names": self.known_face_names}, f)
            
            QMessageBox.information(self, "Success", f"Successfully deleted {name}.")
            self.update_dashboard()

    def delete_records_for_day(self):
        date, ok = QInputDialog.getText(self, "Delete Records for a Specific Day", "Enter the date (YYYY-MM-DD):")
        
        if ok and date:
            attendance_data = self.load_attendance()
            updated_data = [record for record in attendance_data if record["date"] != date]
            
            self.save_attendance(updated_data)
            QMessageBox.information(self, "Success", f"Attendance records for {date} deleted.")
            self.update_dashboard()

    def record_attendance(self, name):
     current_time = datetime.now()
     attendance_data = self.load_attendance()

    # Check if the person has already been marked as present today
     today = current_time.strftime("%Y-%m-%d")
     if any(record['name'] == name and record['date'] == today for record in attendance_data):
        self.status_label.setText(f"{name} has already been marked present today.")
        return
    
    # If not already present, create a new attendance record
     new_record = {
        "name": name,
        "date": today,
        "time": current_time.strftime("%H:%M:%S"),
     }
    
     attendance_data.append(new_record)
     self.save_attendance(attendance_data)

     self.status_label.setText(f"Recorded attendance for {name} at {new_record['time']}")
     self.update_dashboard()


    def update_dashboard(self):
        self.total_students_label.setText(f"Total Students: {len(self.known_face_names)}")
        attendance_data = self.load_attendance()
        today = datetime.now().strftime("%Y-%m-%d")
        present_today = len([record for record in attendance_data if record.get("date") == today])
        self.present_today_label.setText(f"Present Today: {present_today}")
        
        self.attendance_table.setRowCount(len(attendance_data))
        for row, record in enumerate(attendance_data):
            self.attendance_table.setItem(row, 0, QTableWidgetItem(record.get("name", "Unknown")))
            self.attendance_table.setItem(row, 1, QTableWidgetItem(record.get("date", "Unknown")))

    def load_registered_faces(self):
        try:
            with open("registered_faces.json", "r") as f:
                data = json.load(f)
                self.known_face_encodings = np.array(data.get("encodings", []))
                self.known_face_names = data.get("names", [])
        except (FileNotFoundError, json.JSONDecodeError):
            self.known_face_encodings = []
            self.known_face_names = []

    def load_attendance(self):
        try:
            with open("attendance.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_attendance(self, data):
        with open("attendance.json", "w") as f:
            json.dump(data, f)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AttendanceSystem()
    window.show()
    sys.exit(app.exec())

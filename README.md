# Facial Recognition Attendance System

## 📌 Overview
The Facial Recognition Attendance System is a PyQt-based application that automates attendance tracking using facial recognition. It allows administrators to register faces, mark attendance, and manage attendance records efficiently.

## 🚀 Features
- 🖼️ **Face Registration**: Register new users with their facial data.
- 📸 **Real-time Recognition**: Automatically detect and recognize faces.
- 📝 **Attendance Logging**: Log attendance with timestamps.
- 🗑️ **Face Deletion**: Remove registered faces from the system.
- 📅 **Attendance Record Management**: View and delete attendance records for specific days.

## 🛠️ Technologies Used
- **Python**: Core programming language.
- **PyQt6**: GUI framework for desktop applications.
- **OpenCV**: Image processing and camera handling.
- **Face Recognition**: Facial encoding and matching.
- **NumPy**: Data manipulation and storage.
- **JSON**: Persistent storage for registered faces and attendance records.

## 📂 Folder Structure
```
Facial_Recognition_Attendance/
├── main.py  # Main application file
├── registered_faces.json  # Stores encoded face data
├── attendance.json  # Stores attendance records
├── assets/  # UI icons and other assets
└── README.md  # Project documentation
```

## 💻 Installation & Setup
### 1️⃣ Clone the Repository:
```sh
git clone https://github.com/yourusername/facial-recognition-attendance.git
cd facial-recognition-attendance
```

### 2️⃣ Install Dependencies:
```sh
pip install -r requirements.txt
```

### 3️⃣ Run the Application:
```sh
python main.py
```

## 🛡️ Security & Privacy
This application does not store images; it only saves face encodings for recognition. Attendance logs are stored locally in JSON format.

## 🛠️ Future Enhancements
- 🔒 **User Authentication**: Add login system for administrators.
- 📊 **Data Analytics**: Provide insights into attendance trends.
- ☁️ **Cloud Storage**: Store data securely on a remote server.

## 📝 License
This project is licensed under the MIT License.

---
**Developed by [Anandhu](https://github.com/anandhu2311c)**


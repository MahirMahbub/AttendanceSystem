# AttendanceSystem
An IoT-Based Attendance System and Access Management System. 
* JWT authentication-based backend server.
* Functional admin dashboard.
* Two side devices for sign-in and sign-out.
* *(Future Scope)* Face-Detection-based access management.
* *(Future Scope)* Detection of temporal time(suspicious present time) with total work hour visualization.

# IoT Devices
* ESP8266/ NodeMCU
* MFRC522 RFID
* Servo motor
* I2C LCD Display (16 * 2)
* Bread Board
* Jumper wires

# How to Run
## Backend
* Create a python virtual environment.
* Active the python virtual environment. 
* Run "pip install -r requirements.txt".
* Run "python manage.py makemigrations".
* Run "python manage.py migrate".
* Run "python manage.py createsuperuser" (Then input the email and password).
* Run "python manage.py runserver".

## IoT
* Setup the config(Design will be provided soon).
* Run rfid_access_control_in.ino from sign-in side.
* Run rfid_access_control_out.ino from sign-out side.

  

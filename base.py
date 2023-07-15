import sys
import argparse
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QVBoxLayout, QLabel, QLineEdit, QMessageBox
from PyQt5.QtCore import QTimer
from seleni import automate_data_entry
import sqlite3
from view_clients import MainWindow
from update_client import ShowUpdateClient
import os



parser = argparse.ArgumentParser()
parser.add_argument('--name', type=str, default='Safe')
parser.add_argument('--chromedriver', type=str, default='drivers/chromedriver')
args = parser.parse_args()

Myapp = QApplication([])
Myapp.setStyle('Fusion')
Myapp.setApplicationName(args.name)


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 300, 600)

        self.name_label = QLabel("Prenume:")
        self.name_input = QLineEdit()
        self.name_input.setObjectName("name_input")
        self.name_label.setObjectName("name_label")
        self.name_input.setFixedSize(300, 30)

        self.surname_label = QLabel("Nume:")
        self.surname_input = QLineEdit()
        self.surname_label.setObjectName("surname_label")
        self.surname_input.setObjectName("surname_input")
        self.surname_input.setFixedSize(300, 30)

        self.idnp_label = QLabel("IDNP:")
        self.idnp_input = QLineEdit()
        self.idnp_label.setObjectName("idnp_label")
        self.idnp_input.setObjectName("idnp_input")
        self.idnp_input.setMaxLength(13)
        self.idnp_input.setFixedSize(300, 30)

        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_label.setObjectName("email_label")
        self.email_input.setObjectName("email_input")
        self.email_input.setFixedSize(300, 30)

        self.customer_data = QTextEdit()
        self.customer_data.setObjectName("customer_data")
        self.customer_data.setFixedSize(300, 100)
        self.submit_button = QPushButton("Salveaza Datele")
        self.submit_button.setObjectName("submit_button")
        self.update_button = QPushButton("Update client data")
        self.update_button.setObjectName("update_button")
        self.submit_button.setFixedSize(300, 50)  # Set a fixed size for the button

        self.clear_button = QPushButton("Clear Data")
        self.clear_button.setObjectName("clear_button")
        self.clear_button.setObjectName("clear_button")
        self.clear_button.clicked.connect(self.clear_data)
        self.clear_button.setFixedSize(300, 30)

        self.submit_button.clicked.connect(self.submit_data)
        self.update_button.clicked.connect(self.show_update_client)
        self.update_button.setFixedSize(300, 50)  # Set a fixed size for the button

        self.show_clients_button = QPushButton("Lista de clienti")
        self.show_clients_button.setObjectName("show_clients_button")
        self.show_clients_button.clicked.connect(self.show_clients)
        self.show_clients_button.setFixedSize(300, 50)

        self.start_button = QPushButton("Start Automation")
        self.start_button.clicked.connect(self.start_automation)  # Connect start_automation method
        self.start_button.setObjectName("start_button")
        self.start_button.setFixedSize(300, 50)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.surname_label)
        layout.addWidget(self.surname_input)
        layout.addWidget(self.idnp_label)
        layout.addWidget(self.idnp_input)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.customer_data)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.show_clients_button)
        layout.addWidget(self.update_button)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def start_automation(self):
        chromedriver_path = args.chromedriver 
        automate_data_entry(chromedriver_path)

    def clear_data(self):
        self.name_input.clear()
        self.surname_input.clear()
        self.idnp_input.clear()
        self.email_input.clear()
        self.customer_data.clear()

    def show_clients(self):
        try:
            self.mainWindow = MainWindow()
            self.mainWindow.showWindow()
        except Exception as e:
            print(f"An exception occurred: {e}")

    def show_update_client(self):
        self.mainWindow = ShowUpdateClient()
        self.mainWindow.show()

    def show_messageBox(self):
        # Create a message box dialog
        self.msgBox = QMessageBox()
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setText("Invalid input data")
        self.msgBox.setWindowTitle("Warning!")
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        self.msgBox.setStyleSheet("QPushButton { min-width: 200px; }")
        self.msgBox.exec()

    def connect_to_db(self):
        conn = sqlite3.connect('database/ClientAdd.db')
        return conn

    def save_data(self, name, surname, idnp, email):
        # save the data to the database
        conn = sqlite3.connect('database/ClientAdd.db')
        c = conn.cursor()
        c.execute(f"INSERT INTO Clients (first_name, last_name, idnp, email, date_add, status) VALUES ('{name}', '{surname}', '{idnp}','{email}', '{datetime.now()}', 'PENDING')")
        conn.commit()
        conn.close()

    def submit_data(self):
        name = self.name_input.text()
        surname = self.surname_input.text()
        idnp = self.idnp_input.text()
        email = self.email_input.text()

        if name and surname and idnp and len(idnp) == 13:
            customer_data = f"{name} {surname} {idnp} {email}"
            self.customer_data.append(customer_data)
            self.save_data(name, surname, idnp, email)

            now = datetime.now()
            recording_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
            if now < recording_time:
                delta_t = recording_time - now
                recording_timer = QTimer()
                recording_timer.timeout.connect(lambda: self.record_data(name, surname, idnp, email))
                recording_timer.start(int(delta_t.total_seconds() * 1000))
        else:
            self.show_messageBox()
    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    base_path = os.path.dirname(os.path.abspath(__file__))
    css_path = 'E:/ClientAdd-master/design/design_ui.css'
    app.setStyleSheet(open(css_path).read())
    ex.setStyleSheet("background-color: black;")
    ex.name_input.setStyleSheet("background-color: white;")
    ex.surname_input.setStyleSheet("background-color: white;")
    ex.idnp_input.setStyleSheet("background-color: white;")
    ex.email_input.setStyleSheet("background-color: white;")
    ex.customer_data.setStyleSheet("background-color: white;")
    ex.show()
    sys.exit(app.exec_())

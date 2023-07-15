import sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QVBoxLayout, QLabel, QLineEdit, QMessageBox,QTableWidget, QHBoxLayout
from PyQt5.QtWidgets import QComboBox
import sqlite3
from fonts import fonts


class ShowUpdateClient(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        
        self.old_title = QLabel("Old Client Data")
        self.old_title.setFont(fonts.titleFont)

        self.old_name_label = QLabel("First Name:")
        self.old_name_input = QLineEdit()
        self.old_name_input.setReadOnly(True)
        
        self.old_surname_label = QLabel("Last Name:")
        self.old_surname_input = QLineEdit()
        self.old_surname_input.setReadOnly(True)
        
        self.old_idnp_label = QLabel("IDNP:")

        self.idnp_combo_box = QComboBox()
        self.idnp_combo_box.currentIndexChanged.connect(self.get_client_from_db)

        # Connect to the SQLite database
        conn = sqlite3.connect('database/ClientAdd.db')
        cursor = conn.cursor()

        # Execute a query to retrieve data from the database
        cursor.execute("SELECT DISTINCT idnp FROM Clients")
        for row in cursor.fetchall():
            value = row[0]
            self.idnp_combo_box.addItem(value)
        #rows = cursor.fetchall()

        #self.select_old_button = QPushButton("Select client data")
        
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.old_title)
        left_layout.addWidget(self.old_name_label)
        left_layout.addWidget(self.old_name_input)
        left_layout.addWidget(self.old_surname_label)
        left_layout.addWidget(self.old_surname_input)
        left_layout.addWidget(self.old_idnp_label)
        left_layout.addWidget(self.idnp_combo_box)
        #left_layout.addWidget(self.select_old_button)
        left_layout.setContentsMargins(10, 10, 10, 10)

        #===============================================
        # right laytout
        self.new_title = QLabel("New Client Data")
        self.new_title.setFont(fonts.titleFont)

        self.new_name_label = QLabel("First Name:")
        self.new_name_input = QLineEdit()
        
        self.new_surname_label = QLabel("Last Name:")
        self.new_surname_input = QLineEdit()
        
        self.new_idnp_label = QLabel("IDNP:")
        self.new_idnp_input = QLineEdit()
        self.new_idnp_input.setMaxLength(13)

        self.update_client_button = QPushButton("Update Client Data")
        self.update_client_button.clicked.connect(self.update_client_data)
        
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.new_title)
        right_layout.addWidget(self.new_name_label)
        right_layout.addWidget(self.new_name_input)
        right_layout.addWidget(self.new_surname_label)
        right_layout.addWidget(self.new_surname_input)
        right_layout.addWidget(self.new_idnp_label)
        right_layout.addWidget(self.new_idnp_input)
        right_layout.addWidget(self.update_client_button)
        right_layout.setContentsMargins(10, 10, 10, 10)

        #main layout
        mainLayout = QHBoxLayout()
        mainLayout.addLayout(left_layout)
        mainLayout.addLayout(right_layout)

        self.setLayout(mainLayout)

    def get_client_from_db(self):
        conn = sqlite3.connect('database/ClientAdd.db')
        cursor = conn.cursor()
        current_text = self.idnp_combo_box.currentText()
        cursor.execute("SELECT first_name, last_name from Clients WHERE idnp = ?", (current_text,))
        result = cursor.fetchone()

        if result:
            self.old_name_input.setText(result[0])
            self.old_surname_input.setText(result[1])

    def update_client_data(self):
        if self.old_name_input.text() == self.new_name_input.text() and self.old_surname_input.text() == self.new_surname_input.text() \
        and self.idnp_combo_box.currentText() == self.new_idnp_input.text():
            self.show_messageBox("The old data and new data are the same!\nNo update needed.")
        elif self.new_name_input.text() == '' or self.new_surname_input.text() == '' or self.new_idnp_input.text() == '':
            self.show_messageBox("Please input all principal data!")
        else:
            conn = sqlite3.connect('database/ClientAdd.db')
            cursor = conn.cursor()
            current_text = self.idnp_combo_box.currentText()
            cursor.execute(f"UPDATE Clients SET first_name = '{self.new_name_input.text()}', last_name = '{self.new_surname_input.text()}'\
                           , idnp = '{self.new_idnp_input.text()}' WHERE idnp = '{current_text}'")
            conn.commit()
            self.show_messageBox(f"Client updated: {self.new_idnp_input.text()}, {self.new_name_input.text()}, {self.new_surname_input.text()}")

    def show_messageBox(self, msg):
        # Create a message box dialog
        self.msgBox = QMessageBox()
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setText(msg)
        self.msgBox.setWindowTitle("Inform")
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        self.msgBox.exec()


if __name__ == '__main__':
     app = QApplication(sys.argv)
     ex = ShowUpdateClient()
     ex.show()
     sys.exit(app.exec_())

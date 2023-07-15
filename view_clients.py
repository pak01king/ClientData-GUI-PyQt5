import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QVBoxLayout,QWidget,QMessageBox
from PyQt5.QtCore import QFile, QTextStream
import sqlite3

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('View Clients List')
        self.setGeometry(100, 100, 800, 600)

        # Create a table widget
        self.tableWidget = QTableWidget()
        self.setCentralWidget(self.tableWidget)

        # Connect to the SQLite database
        conn = sqlite3.connect('database/ClientAdd.db')
        cursor = conn.cursor()

        # Execute a query to retrieve data from the database
        cursor.execute("SELECT * FROM Clients")
        rows = cursor.fetchall()

        # Set the table widget properties
        num_rows = len(rows)
        num_columns = len(rows[0])
        self.tableWidget.setRowCount(num_rows)
        self.tableWidget.setColumnCount(num_columns)

        # Set the column titles
        columnTitles = ['ID', 'First Name', 'Last Name', 'IDNP', 'email', 'Date Added', 'Status']
        self.tableWidget.setHorizontalHeaderLabels(columnTitles)
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Populate the table widget with data from the database
        for i in range(num_rows):
            for j in range(num_columns):
                data = str(rows[i][j])
                item = QTableWidgetItem(data)
                self.tableWidget.setItem(i, j, item)

        # Resize the columns to fit the contents
        self.tableWidget.resizeColumnsToContents()
        # Hide the row and column numbers
        self.tableWidget.verticalHeader().setVisible(False)

        # Set the selection behavior to select entire rows
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)

        # Create the delete button
        self.delete_button = QPushButton("Delete")
        # Connect the clicked signal to the deleteSelectedClient slot
        self.delete_button.clicked.connect(self.deleteSelectedClient)

        # Create a vertical layout and add the table widget and delete button to it
        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)
        layout.addWidget(self.delete_button)

        # Set the vertical layout as the central widget of the main window
        # Set the layout as the central widget of the main window
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def deleteSelectedClient(self):
    # Get the selected row(s)
      selectedRows = self.tableWidget.selectionModel().selectedRows()
    # If there are selected rows, delete the clients
      if selectedRows:
        # Connect to the SQLite database
        if not selectedRows:
            QMessageBox.critical(self, "Error", "Please select at least one client to delete")
            return
         
        # Ask the user to confirm the deletion
        reply = QMessageBox.question(self, "Confirmare", "Sigur doriți să ștergeți clientul selectat?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return    
        
        conn = sqlite3.connect('database/ClientAdd.db')
        cursor = conn.cursor()

        # Build a list of client IDs to delete
        client_ids = []
        for row in selectedRows:
            client_id = self.tableWidget.item(row.row(), 0).text()
            client_ids.append(client_id)

        # Delete all clients in the list
        placeholders = ','.join('?' * len(client_ids))
        cursor.execute("DELETE FROM Clients WHERE id_client IN ({})".format(placeholders), client_ids)
        
        

        # Commit the changes and close the database connection
        conn.commit()
        conn.close()

        # Remove the selected rows from the table widget
        for row in reversed(selectedRows):
            self.tableWidget.removeRow(row.row())

    
    

    # method which will show the window
    def showWindow(self):
        self.show()
        
        
        

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

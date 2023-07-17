# Automatisation GUI (PyQt5)
The UI created in python, application aims to automate some data from the database and more on site.
This code appears to be a Python script for a graphical user interface (GUI) application using PyQt5. It provides a form for users to enter client data such as first name, last name, ID number, and email. The entered data is validated, saved to an SQLite database, and displayed in a QTextEdit widget.

The GUI contains various buttons for different actions, such as saving the data, clearing the input fields, showing a list of clients, updating client data, and starting an automation process using Selenium for data entry.

The script also includes command-line arguments for customization, such as specifying the application name and the path to the ChromeDriver executable.

The overall structure of the code follows the object-oriented programming (OOP) paradigm, with the main application logic contained within the MyApp class. It includes methods for initializing the GUI, handling button clicks, interacting with the database, and displaying message boxes for warnings or notifications.

In addition to the main script, there are imports from other modules (seleni, view_clients, update_client) and the necessary import statements for the required libraries and modules.


the warning in the file seleni.py remember you can replace with other different flows, the site in the code is only for testing.

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from airports_input_window import AirportInputWindow  # Import the second window class

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 400, 300)

        self.button = QPushButton("Open Second Window", self)
        self.button.setGeometry(100, 100, 200, 50)
        self.button.clicked.connect(self.open_second_window)

    def open_second_window(self):
        self.second_window = AirportInputWindow()  # Create an instance of SecondWindow
        self.second_window.show()  # Show the second window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

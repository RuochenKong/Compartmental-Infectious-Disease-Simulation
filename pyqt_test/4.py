import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton

class RemoveWidgetDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remove Widget Example")
        self.setGeometry(100, 100, 400, 200)

        self.initUI()

    def initUI(self):
        # Central widget and layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        # Input widget to be removed
        self.input_widget = QLineEdit(self)
        self.input_widget.setPlaceholderText("Type something here...")
        self.layout.addWidget(self.input_widget)

        # Button to remove the input widget
        self.remove_button = QPushButton("Remove Input Widget", self)
        self.remove_button.clicked.connect(self.remove_input_widget)
        self.layout.addWidget(self.remove_button)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def remove_input_widget(self):
        if self.input_widget:  # Check if the widget exists
            self.layout.removeWidget(self.input_widget)  # Remove widget from layout
            self.input_widget.deleteLater()  # Schedule widget for deletion
            self.input_widget = None  # Set to None to avoid repeated deletion

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = RemoveWidgetDemo()
    demo.show()
    sys.exit(app.exec_())

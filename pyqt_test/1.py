import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit

class DynamicInputApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create the main layout
        self.layout = QVBoxLayout()

        # Create and add the button to the layout
        self.button = QPushButton("Add Input Line")
        self.button.clicked.connect(self.add_input_line)
        self.layout.addWidget(self.button)

        # Set the layout for the main window
        self.setLayout(self.layout)

        self.setWindowTitle("Dynamic Input Lines")
        self.setGeometry(100, 100, 300, 200)

    def add_input_line(self):
        # Create a new QLineEdit and add it to the layout
        new_input = QLineEdit()
        self.layout.addWidget(new_input)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynamicInputApp()
    window.show()
    sys.exit(app.exec_())

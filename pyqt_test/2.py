import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel

class DynamicInputApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create the main vertical layout
        self.main_layout = QVBoxLayout()

        # Create and add the button to the main layout
        self.button = QPushButton("Add Input Line")
        self.button.clicked.connect(self.add_input_row)
        self.main_layout.addWidget(self.button)

        # Set the layout for the main window
        self.setLayout(self.main_layout)

        self.setWindowTitle("Dynamic Input Rows")
        self.setGeometry(100, 100, 400, 300)

    def add_input_row(self):
        # Create a horizontal layout for the new row
        row_layout = QHBoxLayout()

        # Create a label and input line
        label = QLabel("Description:")
        input_line = QLineEdit()

        # Add the label and input line to the horizontal layout
        row_layout.addWidget(label)
        row_layout.addWidget(input_line)

        # Add the horizontal layout to the main vertical layout
        self.main_layout.addLayout(row_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynamicInputApp()
    window.show()
    sys.exit(app.exec_())

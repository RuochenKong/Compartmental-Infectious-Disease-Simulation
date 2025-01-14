import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dynamic Input Lines")
        self.setGeometry(100, 100, 400, 300)

        # Main layout for the window
        self.main_layout = QVBoxLayout(self)

        # List to keep track of the input fields and remove buttons
        self.input_lines = []

        # Button to add new input line
        self.add_button = QPushButton("Add Input Line", self)
        self.add_button.clicked.connect(self.add_input_line)

        # Add the add button to the main layout
        self.main_layout.addWidget(self.add_button)

    def add_input_line(self):
        # Create a new input line with day and widgets
        day = len(self.input_lines) + 1  # Day starts at 1 and increments with each line

        line_widget = QWidget(self)
        line_layout = QHBoxLayout(line_widget)

        # Day label
        day_label = QLabel(f"Day {day}", self)

        # Input field
        input_field = QLineEdit(self)

        # Remove button
        remove_button = QPushButton("Remove", self)
        remove_button.clicked.connect(lambda: self.remove_input_line(line_widget, day))

        # Add widgets to line layout
        line_layout.addWidget(day_label)
        line_layout.addWidget(input_field)
        line_layout.addWidget(remove_button)

        # Add the line to the main layout
        self.main_layout.addWidget(line_widget)

        # Track the line and its components
        self.input_lines.append((line_widget, day_label, input_field, remove_button))

    def remove_input_line(self, line_widget, day):
        # Remove the line widget from the layout
        line_widget.deleteLater()

        # Remove the line from the list
        self.input_lines = [line for line in self.input_lines if line[0] != line_widget]

        # Update the day of subsequent lines
        for i, (widget, day_label, input_field, remove_button) in enumerate(self.input_lines):
            # Update the day number of subsequent lines
            new_day = i + 1
            day_label.setText(f"Day {new_day}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

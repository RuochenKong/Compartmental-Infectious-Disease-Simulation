import sys
import subprocess
from json.encoder import INFINITY

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox,
    QCheckBox, QHBoxLayout, QSpinBox, QDesktopWidget, QComboBox
)
from PyQt5.QtCore import Qt

from r0_input_window import R0InputWindow
from airports_input_window import AirportInputWindow


DES2PARAM = {'Random Seed': 'seed',
             'Days to simulate': 'days_of_simulation',
             'Number of total runs': 'total_runs',
             'Number of threads': 'num_threads',
             'Output Directory': 'output_dir',
             'Save spreading history': 'do_spread',
             'Save logging information': 'do_log'}

class InputPlatform(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Simulation Set Up")

        # Create layout
        self.layout = QVBoxLayout()

        # Input fields
        self.input_line = []

        self.add_integer_input('Random Seed')
        self.add_integer_input('Days to simulate')
        self.add_integer_input('Number of total runs')
        self.add_integer_input('Number of threads')
        self.add_r0_input()

        self.add_check_box('Save spreading history')
        self.add_check_box('Save logging information')

        self.add_output_dir_input()

        # Save button
        self.save_button = QPushButton("Save parameters")
        self.save_button.clicked.connect(self.save_to_file)
        self.layout.addWidget(self.save_button)

        # Run button
        self.run_button = QPushButton("Start simulation")
        self.run_button.clicked.connect(self.run_simulation)
        self.layout.addWidget(self.run_button)

        # Set layout
        self.setLayout(self.layout)
        self.setWindowTitle("Disease Input Airports")
        self.setGeometry(200, 200, 700, 200)
        self.center()  # Call the method to center the widget

    def center(self):
        # Get the geometry of the primary screen
        screen_geometry = QDesktopWidget().availableGeometry()
        window_geometry = self.frameGeometry()

        # Calculate the center point of the screen
        screen_center = screen_geometry.center()
        screen_center.setY(max(100, screen_center.y() - 200))
        screen_center.setX(max(100, screen_center.x() - 700))

        # Move the window's center to the screen's center
        window_geometry.moveCenter(screen_center)

        # Move the top-left corner of the window to align with the new center
        self.move(window_geometry.topLeft())

    def add_r0_input(self):
        row_layout = QHBoxLayout()

        description = QLabel("Spread chance per day")
        description.setFixedWidth(300)
        description.setAlignment(Qt.AlignRight)

        push_button = QPushButton("Set up",self)
        push_button.clicked.connect(self.open_r0_window)
        push_button.setFixedWidth(150)

        row_layout.addWidget(description)
        row_layout.addWidget(push_button)

        self.layout.addLayout(row_layout)

    def add_infectious_source_input(self):
        row_layout = QHBoxLayout()

        description = QLabel("Spread source")
        description.setFixedWidth(300)
        description.setAlignment(Qt.AlignRight)

        combo_box = QComboBox(self)
        combo_box.addItems(["Random", "Airports"])


    def open_r0_window(self):
        self.r0_window = R0InputWindow()
        self.r0_window.show()

    def open_airport_source_window(self):
        self.airport_source_window = AirportInputWindow()
        self.airport_source_window.show()

    def add_integer_input(self, label, minV=None):
        row_layout = QHBoxLayout()

        description = QLabel(label)
        description.setFixedWidth(300)
        description.setAlignment(Qt.AlignRight)

        input_line = QSpinBox(self)
        input_line.setFixedWidth(150)
        if minV is not None: input_line.setMinimum(minV)
        defaultV = 0 if minV is None else minV
        input_line.setValue(defaultV)

        row_layout.addWidget(description)
        row_layout.addWidget(input_line)

        self.layout.addLayout(row_layout)

        # Store data
        self.input_line.append({'description': description, 'input': input_line})

    def add_check_box(self, label):
        row_layout = QHBoxLayout()

        description = QLabel(label)
        description.setFixedWidth(300)
        description.setAlignment(Qt.AlignRight)

        checkbox = QCheckBox(self)
        checkbox.setFixedWidth(150)

        row_layout.addWidget(description)
        row_layout.addWidget(checkbox)

        self.layout.addLayout(row_layout)

    def add_output_dir_input(self):
        row_layout = QHBoxLayout()

        description = QLabel('Output Directory')
        description.setFixedWidth(300)
        description.setAlignment(Qt.AlignRight)

        input_line = QLineEdit(self)
        input_line.setFixedWidth(150)

        row_layout.addWidget(description)
        row_layout.addWidget(input_line)

        self.layout.addLayout(row_layout)

    def run_simulation(self):
        # subprocess.Popen(["python", "mkypox_main.py"])
        print('Not yet implemented')

    def save_to_file(self):
        # Get values from input fields
        data = {label: input_field.text() for label, input_field in self.inputs.items() if input_field.text().strip()}

        # Add checkbox value only if checked
        if self.checkbox.isChecked():
            data["do_log"] = "True"

        if not data:
            QMessageBox.warning(self, "Warning", "No data to save. All fields are empty.")
            return

        # Define fixed file path
        file_name = "params"

        try:
            # Save data to file
            with open(file_name, "w") as file:
                for key, value in data.items():
                    file.write(f"{key}={value}\n")

            # Confirmation message
            QMessageBox.information(self, "Success", f"Parameters saved to {file_name}!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save the parameters: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InputPlatform()
    window.show()
    sys.exit(app.exec_())

import os
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
from random_src_input_window import RandomSrcInputWindow


DES2PARAM = {'Random Seed': 'seed',
             'Days to simulate': 'days_of_simulation',
             'Number of total runs': 'total_runs',
             'Number of threads': 'num_threads',
             'Output Directory': 'output_dir',
             'Census region level':'region_level',
             'Save region level output': 'do_region',
             'Save case level output': 'do_case'}

class InputPlatform(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Simulation Set Up")

        self.r0_window = R0InputWindow()
        self.airport_source_window = AirportInputWindow()
        self.ramdom_source_window = RandomSrcInputWindow()

        # Create layout
        self.layout = QVBoxLayout()

        # Input fields
        self.input_line = []

        self.add_integer_input('Random Seed')
        self.add_integer_input('Days to simulate',1)
        self.add_integer_input('Number of total runs',1)
        self.add_integer_input('Number of threads',1)
        self.add_r0_input()
        self.add_region_level_row()
        self.add_infectious_source_input()

        self.add_check_box('Save region level output')
        self.add_check_box('Save case level output')

        self.add_output_dir_input()

        # Save button
        self.save_button = QPushButton("Save parameters")
        self.save_button.clicked.connect(self.save_to_file)
        self.layout.addWidget(self.save_button)

        # Select Type of Approach and Run
        self.add_approach_run_row()

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
        self.input_line.append({'description': description, 'input': push_button})

    def add_infectious_source_input(self):
        row_layout = QHBoxLayout()

        description = QLabel("Spread source")
        description.setFixedWidth(300)
        description.setAlignment(Qt.AlignRight)

        combo_box = QComboBox(self)
        combo_box.addItems(["Select an option", "Random", "Specified Airports"])
        combo_box.setFixedWidth(150)

        combo_box.currentIndexChanged.connect(self.handle_selection)

        row_layout.addWidget(description)
        row_layout.addWidget(combo_box)
        self.layout.addLayout(row_layout)

        self.input_line.append({'description': description, 'input': combo_box})

    def add_approach_run_row(self):
        row_layout = QHBoxLayout()

        description = QLabel("Approach Type")
        description.setFixedWidth(130)
        # description.setAlignment(Qt.AlignRight)

        combo_box = QComboBox(self)
        combo_box.addItems(["Select an option", "Naive", "Statistical"])
        combo_box.setFixedWidth(150)

        run_button = QPushButton("Start simulation")
        run_button.clicked.connect(self.run_simulation)

        row_layout.addWidget(description)
        row_layout.addWidget(combo_box)
        row_layout.addWidget(run_button)

        self.layout.addLayout(row_layout)

        self.input_line.append({'description': description, 'input': combo_box})

    def add_region_level_row(self):
        row_layout = QHBoxLayout()

        description = QLabel("Census region level")
        description.setFixedWidth(300)
        description.setAlignment(Qt.AlignRight)

        combo_box = QComboBox(self)
        combo_box.addItems(["Select an option", "Census Block Group", "Census Tract", 'County'])
        combo_box.setFixedWidth(150)

        row_layout.addWidget(description)
        row_layout.addWidget(combo_box)

        self.layout.addLayout(row_layout)

        self.input_line.append({'description': description, 'input': combo_box})

    def handle_selection(self, index):
        try:
            self.r0_window.close()
        except:  pass

        # Handle combo box selection
        if index == 1: # Option 1 selected
            try:
                self.airport_source_window.close()
            except: pass
            self.ramdom_source_window.show()
        elif index == 2:  # Option 2 selected
            try:
                self.ramdom_source_window.close()
            except: pass
            self.airport_source_window.show()

    def open_r0_window(self):
        self.r0_window.show()

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

        # Store data
        self.input_line.append({'description': description, 'input': checkbox})

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

        # Store data
        self.input_line.append({'description': description, 'input': input_line})

    def run_simulation(self):
        # subprocess.Popen(["python", "mkypox_main.py"])
        approach_type = None
        for row in self.input_line:
            description = row['description'].text()
            if description == 'Approach Type':
                input_value = row['input']
                approach_type = input_value.currentText()
                if approach_type == 'Select an option':
                    approach_type = None
                break
        if approach_type is None:
            self.show_invalid_input_error('Missing Simulation Setup', 'No Approach Type Selected')
            return
        simulation_path = '../%s_approach/simulation_main.py'%approach_type.lower()
        param_path = 'GUI_params/params'
        try:
            # Blocking call, waits for simulation to finish
            result = subprocess.run(["python", simulation_path, param_path], capture_output=True)

            if result.returncode == 0:
                self.show_message("Simulation Complete", "The simulation has finished successfully.")
            else:
                self.show_invalid_input_error("Simulation Failed", result.stderr)

        except Exception as e:
            self.show_invalid_input_error("Execution Error", str(e))

    def save_to_file(self):

        filepath = 'GUI_params/params'

        output_lines = []
        r0_file = ''
        src_file = ''

        for row in self.input_line:
            description = row['description'].text()
            label = None
            if description in DES2PARAM:
                label = DES2PARAM[description]

            input_value = row['input']
            if isinstance(input_value, QSpinBox):
                input_value = str(input_value.value())
            elif isinstance(input_value, QCheckBox):
                input_value = 'True' if input_value.isChecked() else 'False'
            elif isinstance(input_value, QLineEdit):
                input_value = input_value.text()
                if input_value == '':
                    input_value = 'output'
                input_value = '../'+input_value
            elif isinstance(input_value, QPushButton):  # This is R0 input
                if not os.path.exists('GUI_params/R0'):
                    self.show_invalid_input_error('Missing parameters', 'No input for spread chance')
                    return
                with open('GUI_params/R0') as f:
                    r0_file = f.read().strip()
            elif description == 'Spread source':  # This is source places
                if input_value.currentText() == 'Select an option':
                    self.show_invalid_input_error('Missing parameters', 'No input for disease sources')
                    return
                if input_value.currentText() == 'Random':
                    if not os.path.exists('GUI_params/random_source'):
                        self.show_invalid_input_error('Missing parameters', 'No input for disease sources')
                        return
                    with open('GUI_params/random_source') as f:
                        src_file = f.read().strip()
                else:
                    if not os.path.exists('GUI_params/airport_sources'):
                        self.show_invalid_input_error('Missing parameters', 'No input for disease sources')
                        return
                    with open('GUI_params/airport_sources') as f:
                        src_file = f.read().strip()
            elif description == 'Census region level':  # This is source places
                if input_value.currentText() == 'Select an option':
                    self.show_invalid_input_error('Missing parameters', 'No input for Census region level')
                    return
                input_value = input_value.currentText()
                if input_value == 'Census Block Group':
                    input_value = 'cbg'
                elif input_value == 'Census Tract':
                    input_value = 'census_tract'
                else:
                    input_value = 'county'
            if label is not None:
                output_lines.append(label +'='+input_value)

        with open(filepath, 'w') as f:
            f.write('\n'.join(output_lines))
            f.write('\n' + r0_file)
            f.write('\n' + src_file)

        self.show_save_popup(filepath)

    def show_invalid_input_error(self, main_text, informative_text):
        error_popup = QMessageBox(self)
        error_popup.setIcon(QMessageBox.Critical)  # Critical icon for errors
        error_popup.setWindowTitle("Error")  # Title of the popup
        error_popup.setText(main_text)  # Error message text
        error_popup.setInformativeText(informative_text)  # Additional information
        error_popup.setStandardButtons(QMessageBox.Ok)  # OK button to close the popup
        error_popup.exec_()  # Show the popup

    def show_save_popup(self, file_path):
        # Create a QMessageBox to display the saving path
        message_box = QMessageBox()
        message_box.setFixedWidth(300)
        message_box.setWindowTitle("Save Successful")
        message_box.setText(f"Data has been saved to:\n{file_path}")
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec_()

    def show_message(self, title, msg):
        # Create a QMessageBox to display the saving path
        message_box = QMessageBox()
        message_box.setFixedWidth(300)
        message_box.setWindowTitle(title)
        message_box.setText(msg)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec_()

if __name__ == "__main__":
    if not os.path.exists("GUI_params"):
        os.mkdir("GUI_params")

    for filename in os.listdir("GUI_params"):
        os.remove('GUI_params/%s'%filename)

    app = QApplication(sys.argv)
    app.setStyleSheet("""
        * {
            font-family: "Calibri";
            font-size: 12pt;
        }
    """)
    window = InputPlatform()
    window.show()
    sys.exit(app.exec_())

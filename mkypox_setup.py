import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QCheckBox
)
from PyQt5.QtGui import QFont

class InputPlatform(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Simulation Parameters")

        # Create layout
        self.layout = QVBoxLayout()

        # Input fields
        self.inputs = {}
        variable_descriptions = {'seed': 'Random seed',
                                 'infection_chance_per_day': 'Chance of an Infectious agent to spread per day, sum to R0',
                                 'days_of_simulation': 'Total days to simulate',
                                 'total_runs': 'Numbers of simulation runs',
                                 'num_threads': 'Numbers of simulations running simultaneously',
                                 'list_init_cbg': 'List of Census Block Groups having initial cases',
                                 'num_init_cases': 'Numbers of initial cases per CBG',
                                 'output_dir': 'Folder to store simulation results'}

        label_font = QFont("Arial", 12, QFont.Bold)
        description_font = QFont("Arial", 10, QFont.StyleItalic)

        for label, description in variable_descriptions.items():
            lbl = QLabel(label)
            lbl.setFont(label_font)
            desc = QLabel(f"  {description}")
            desc.setFont(description_font)

            line_edit = QLineEdit()
            self.inputs[label] = line_edit

            self.layout.addWidget(lbl)
            self.layout.addWidget(desc)
            self.layout.addWidget(line_edit)

        # Checkbox for log
        lbl_checkbox = QLabel("do_log")
        lbl_checkbox.setFont(label_font)
        desc_checkbox = QLabel("  Whether enable logging during simulations")
        desc_checkbox.setFont(description_font)
        self.checkbox = QCheckBox()

        self.layout.addWidget(lbl_checkbox)
        self.layout.addWidget(desc_checkbox)
        self.layout.addWidget(self.checkbox)

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

    def run_simulation(self):
        subprocess.Popen(["python", ".\\mkypox_main.py"])

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

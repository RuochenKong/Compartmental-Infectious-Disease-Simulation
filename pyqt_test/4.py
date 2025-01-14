import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QMessageBox


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create Input Boxes Based on Integer")
        self.setGeometry(100, 100, 400, 300)

        # Main layout for the window
        self.main_layout = QVBoxLayout(self)

        # Label to explain the input box
        self.total_day_layout = QHBoxLayout()
        self.instruction_label = QLabel("Days of the Infectious Lasting:")
        self.total_day_layout.addWidget(self.instruction_label)

        # Input box to ask for the number of input fields
        self.input_number_field = QSpinBox(self)  # Use QSpinBox for integer input
        self.input_number_field.setRange(1, 100)  # Set min and max range
        self.input_number_field.setValue(1)  # Set default value to 1
        self.total_day_layout.addWidget(self.input_number_field)

        # Button to trigger the creation of input boxes
        self.create_button = QPushButton("✔️", self)
        self.create_button.clicked.connect(self.create_input_boxes)
        self.total_day_layout.addWidget(self.create_button)

        self.main_layout.addLayout(self.total_day_layout)

        # A layout to hold the dynamically created input boxes
        self.dynamic_layout = QVBoxLayout()
        self.main_layout.addLayout(self.dynamic_layout)

        self.input_rows = []

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_input_row)
        self.main_layout.addWidget(self.save_button)

    def create_input_boxes(self):
        # Clear any previously created input boxes
        for row_layout in self.input_rows:
            for widget in row_layout:
                widget.deleteLater()  # Remove the widget from layout
        self.input_rows.clear()  # Clear the reference list


        # Get the number of input boxes to create
        num_boxes = self.input_number_field.value()

        # Create the specified number of input boxes
        for i in range(num_boxes):
            row_layout = QHBoxLayout()
            label = QLabel(f"Day {i + 1}:", self)
            input_field = QLineEdit(self)
            row_layout.addWidget(label)
            row_layout.addWidget(input_field)

            self.dynamic_layout.addLayout(row_layout)

            self.input_rows.append([label, input_field])

    def save_input_row(self):
        if not os.path.exists("GUI_params"):
            os.mkdir("GUI_params")

        filepath = 'GUI_params/R0'

        probs = []
        for row in self.input_rows:
            val = row[1].text()
            if val == '' or float(val) < 0 or float(val) >= 1:
                self.show_invalid_input_error(row[0].text()[:-1])
                return
            probs.append(str(float(val)))

        with open(filepath, 'w') as f:

            # Ignore empty inputs
            if len(probs) == 0: return

            f.write('infection_chance_per_day=')
            f.write('/'.join(probs))

        self.show_save_popup(filepath)

    def show_invalid_input_error(self, day):
        error_popup = QMessageBox(self)
        error_popup.setIcon(QMessageBox.Critical)  # Critical icon for errors
        error_popup.setWindowTitle("Error")  # Title of the popup
        error_popup.setText(f"Invalid input for {day}")  # Error message text
        error_popup.setInformativeText("Please input a value in range (0,1)")  # Additional information
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

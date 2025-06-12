import os
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QDesktopWidget, QPushButton, QLineEdit, QMessageBox,
                             QSpinBox, QLabel)

class R0InputWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 500, 100)

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

        self.setWindowTitle("Disease R0")
        self.center()  # Call the method to center the widget

    def center(self):
        # Get the geometry of the primary screen
        screen_geometry = QDesktopWidget().availableGeometry()
        window_geometry = self.frameGeometry()

        # Calculate the center point of the screen
        screen_center = screen_geometry.center()
        screen_center.setY(max(100, screen_center.y() - 300))

        # Move the window's center to the screen's center
        window_geometry.moveCenter(screen_center)

        # Move the top-left corner of the window to align with the new center
        self.move(window_geometry.topLeft())

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
            label = QLabel(f"Day {i + 1}", self)
            label.setFixedWidth(100)

            input_field = QLineEdit(self)
            input_field.setText("0")
            row_layout.addWidget(label)
            row_layout.addWidget(input_field)

            self.dynamic_layout.addLayout(row_layout)

            self.input_rows.append([label, input_field])

    def save_input_row(self):

        filepath = 'GUI_params/R0'

        probs = []
        for row in self.input_rows:
            val = row[1].text()
            try:
                val = float(val)
                if float(val) < 0:
                    self.show_invalid_input_error(row[0].text())
                    return
                probs.append(str(float(val)))
            except:
                self.show_invalid_input_error(row[0].text()[:-1])
                return

        # Ignore empty inputs
        if len(probs) == 0: return

        with open(filepath, 'w') as f:
            f.write('infection_chance_per_day=')
            f.write('/'.join(probs))

        self.show_save_popup(filepath)

    def show_invalid_input_error(self, day):
        error_popup = QMessageBox(self)
        error_popup.setIcon(QMessageBox.Critical)  # Critical icon for errors
        error_popup.setWindowTitle("Error")  # Title of the popup
        error_popup.setText(f"Invalid input for {day}")  # Error message text
        error_popup.setInformativeText("Spread probability should not be negative.")  # Additional information
        error_popup.setStandardButtons(QMessageBox.Ok)  # OK button to close the popup

        # Move to center of the screen
        screen_geometry = QDesktopWidget().availableGeometry()
        box_geometry = error_popup.frameGeometry()
        center_point = screen_geometry.center()
        box_geometry.moveCenter(center_point)
        error_popup.move(box_geometry.topLeft())

        error_popup.exec_()  # Show the popup

    def show_save_popup(self, file_path):
        # Create a QMessageBox to display the saving path
        message_box = QMessageBox()
        message_box.setFixedWidth(300)
        message_box.setWindowTitle("Save Successful")
        message_box.setText(f"Data has been saved to:\n{file_path}")
        message_box.setStandardButtons(QMessageBox.Ok)

        # Move to center of the screen
        screen_geometry = QDesktopWidget().availableGeometry()
        box_geometry = message_box.frameGeometry()
        center_point = screen_geometry.center()
        box_geometry.moveCenter(center_point)
        message_box.move(box_geometry.topLeft())

        message_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = R0InputWindow()
    window.show()
    sys.exit(app.exec_())

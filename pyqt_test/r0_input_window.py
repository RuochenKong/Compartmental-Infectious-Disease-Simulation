import os
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QDesktopWidget, QPushButton, QLineEdit, QMessageBox,
                             QComboBox,  QScrollArea, QLabel)
from PyQt5.QtCore import Qt

class R0InputWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.data = [] # List to store input data

    def init_ui(self):
        # Create the main vertical layout
        self.main_layout = QVBoxLayout()

        # A separate layout to hold the input rows
        self.input_layout = QVBoxLayout()
        self.main_layout.addLayout(self.input_layout)

        # Create and add the button to the main layout
        self.button = QPushButton("+")
        self.button.clicked.connect(self.add_input_row)
        self.main_layout.addWidget(self.button)

        # Create and add the button to save inputs
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_input_row)
        self.main_layout.addWidget(self.save_button)


        # Set the layout for the main window
        self.setLayout(self.main_layout)

        self.setWindowTitle("Disease R0")
        self.setGeometry(200, 200, 500, 200)
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


    def add_input_row(self):
        day = len(self.data) + 1

        # Create a horizontal layout for the new row
        row_widget = QWidget(self)
        row_layout = QHBoxLayout(row_widget)

        # Description
        description_label = QLabel(f"Day {day}", self)

        # Input spread probability
        input_line = QLineEdit()
        input_line.setFixedWidth(200)

        # Create a "Remove Line" button
        remove_button = QPushButton("-")
        remove_button.setFixedWidth(50)
        remove_button.clicked.connect(lambda: self.remove_input_row(row_widget,day))

        # Add the label and input line to the horizontal layout
        row_layout.addWidget(description_label)
        row_layout.addWidget(input_line)
        row_layout.addWidget(remove_button)

        # Add the horizontal layout to the main vertical layout
        self.input_layout.addWidget(row_widget)

        # Store the input row
        self.data.append((row_widget, description_label, input_line, remove_button))

    def remove_input_row(self, row_widget, day):
        # Remove the line widget from the layout
        row_widget.deleteLater()

        # Remove the line from the list
        self.data = [line for line in self.data if line[0] != row_widget]

        # Update the day of subsequent lines
        for i, (widget, day_label, input_field, remove_button) in enumerate(self.data):
            # Update the day number of subsequent lines
            new_day = i + 1
            day_label.setText(f"Day {new_day}")

    def save_input_row(self):
        if not os.path.exists("GUI_params"):
            os.mkdir("GUI_params")

        filepath = 'GUI_params/R0'
        with open(filepath, 'w') as f:
            probs = []
            for row in self.data:
                val = row[2].text()
                if val == '' or float(val) < 0 or float(val) >= 1:
                    self.show_invalid_input_error(row[1].text())
                    return
                probs.append(str(float(val)))

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
    window = R0InputWindow()
    window.show()
    sys.exit(app.exec_())

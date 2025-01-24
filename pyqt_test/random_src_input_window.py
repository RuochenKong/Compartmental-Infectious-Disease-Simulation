import os
import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QDesktopWidget, QPushButton, QSpinBox, QMessageBox,QCheckBox,
                             QComboBox,  QScrollArea, QLabel)
from PyQt5.QtCore import Qt

class RandomSrcInputWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 350, 100)

        # Main layout for the window
        self.layout = QVBoxLayout(self)
        self.input_line = []
        self.add_check_box('Starts from random airports')
        self.add_integer_input('Number of source locations')
        self.add_integer_input('Number of cases per location')

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_input)
        self.layout.addWidget(self.save_button)

        self.setWindowTitle("Random Disease Source Input")
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

    def add_check_box(self, label):
        row_layout = QHBoxLayout()

        description = QLabel(label)
        description.setFixedWidth(200)
        description.setAlignment(Qt.AlignRight)

        checkbox = QCheckBox(self)
        checkbox.setFixedWidth(50)

        row_layout.addWidget(description)
        row_layout.addWidget(checkbox)

        print(type(checkbox))
        self.layout.addLayout(row_layout)
        # Store data
        self.input_line.append({'description': description, 'input': checkbox})

    def add_integer_input(self, label):
        row_layout = QHBoxLayout()

        description = QLabel(label)
        description.setFixedWidth(200)
        description.setAlignment(Qt.AlignRight)

        input_line = QSpinBox(self)
        input_line.setFixedWidth(50)
        input_line.setMinimum(1)
        input_line.setValue(1)

        row_layout.addWidget(description)
        row_layout.addWidget(input_line)

        self.layout.addLayout(row_layout)

        # Store data
        self.input_line.append({'description': description, 'input': input_line})

    def save_input(self):
        filepath = 'GUI_params/random_source'

        from_airports = ''
        cases = 0
        places = 0
        for row in self.input_line:
            description = row['description'].text()
            input_data = row['input']

            if isinstance(input_data, QCheckBox):
                from_airports = 'True' if input_data.isChecked() else 'False'
                continue

            if description == 'Number of source locations':
                places = input_data.value()
            else:
                cases = input_data.value()

        with open(filepath,'w') as f:
            f.write('from_airport=%s\n'%from_airports)
            f.write('num_init_cases=%s'%('/'.join([str(cases)] * places)))

        self.show_save_popup(filepath)


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
    window = RandomSrcInputWindow()
    window.show()
    sys.exit(app.exec_())

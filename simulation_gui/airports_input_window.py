import os
import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QDesktopWidget, QPushButton, QSpinBox, QMessageBox,
                             QComboBox,  QScrollArea, QLabel)
from PyQt5.QtCore import Qt

AIRPORTS_INFO = {}
tmp_df = pd.read_csv('../src_data/airports_geoinfo.csv')
for k,name,geoid in zip(tmp_df['iata_code'], tmp_df['name'],tmp_df['GeoId']):
    AIRPORTS_INFO[k] = [name,str(geoid)]
AIRPORTS = list(AIRPORTS_INFO.keys())
AIRPORTS.sort()

class AirportInputWindow(QWidget):
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

        self.setWindowTitle("Disease Input Airports")
        self.setGeometry(100, 100, 500, 100)
        self.center()  # Call the method to center the widget

    def center(self):
        # Get the geometry of the primary screen
        screen_geometry = QDesktopWidget().availableGeometry()
        window_geometry = self.frameGeometry()

        # Calculate the center point of the screen
        screen_center = screen_geometry.center()
        screen_center.setY(max(100, screen_center.y() - 300))
        screen_center.setX(max(100, screen_center.x() + 600))

        # Move the window's center to the screen's center
        window_geometry.moveCenter(screen_center)

        # Move the top-left corner of the window to align with the new center
        self.move(window_geometry.topLeft())


    def add_input_row(self):
        # Create a horizontal layout for the new row
        row_layout = QHBoxLayout()

        # Create a scrollable description label
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedWidth(300)  # Set fixed width for the scroll area
        scroll_area.setFixedHeight(50)  # Set fixed height for the scroll area

        # Description
        description_label = QLabel("Select an airport")
        description_label.setAlignment(Qt.AlignRight | Qt.AlignTop)  # Align text to the right & Top
        description_label.setStyleSheet("color: blue;")  # Set text color to red
        description_label.setWordWrap(True)

        # Add the label to the scroll area
        scroll_area.setWidget(description_label)

        # Create a label and input line
        combo_box = QComboBox(self)
        combo_box.addItems(AIRPORTS)
        combo_box.setFixedWidth(150)

        input_line = QSpinBox(self)
        input_line.setMinimum(1)
        input_line.setFixedWidth(100)

        # update description
        combo_box.currentIndexChanged.connect(
            lambda: self.update_description(combo_box, description_label)
        )

        # Create a "Remove Line" button
        remove_button = QPushButton("-")
        remove_button.setFixedWidth(50)
        remove_button.clicked.connect(lambda: self.remove_input_row(row_layout, combo_box, input_line))

        # Add the label and input line to the horizontal layout
        row_layout.addWidget(description_label)
        row_layout.addWidget(combo_box)
        row_layout.addWidget(input_line)
        row_layout.addWidget(remove_button)

        # Add the horizontal layout to the main vertical layout
        self.input_layout.addLayout(row_layout)

        # Store the input row
        self.data.append({"combo_box": combo_box, "input_line": input_line, "description": description_label})

    def remove_input_row(self, row_layout, combo_box, input_line):
        # Remove all widgets in the given row layout
        while row_layout.count():
            widget = row_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        # Remove the row layout itself from the parent layout
        self.input_layout.removeItem(row_layout)

        # Remove the row from collection
        self.data = [row for row in self.data if row["combo_box"] != combo_box]

    def update_description(self, combo_box, description_label):

        # Update the description label based on the selected option
        selected_option = combo_box.currentText()
        description_label.setText(AIRPORTS_INFO.get(selected_option, ["Error"])[0])
        description_label.setStyleSheet("color: black;")  # Set text color to red

    def save_input_row(self):
        filepath = 'GUI_params/airport_sources'
        geoids = []
        cases = []
        for row in self.data:
            combo_value = row["combo_box"].currentText()
            input_value = row["input_line"].value()
            description = row["description"].text()
            if description == 'Select an airport':
                continue

            geoids.append(AIRPORTS_INFO[combo_value][1])
            cases.append(input_value)

        # Ignore empty inputs
        if len(geoids) == 0: return

        with open(filepath, 'w') as f:
            f.write('init_region_id=')
            f.write('/'.join(geoids))
            f.write('\nnum_init_cases=')
            f.write('/'.join(str(case) for case in cases))
            f.write('\nfrom_des=False')

        self.show_save_popup(filepath)

    def show_invalid_input_error(self, airport):
        error_popup = QMessageBox(self)
        error_popup.setIcon(QMessageBox.Critical)  # Critical icon for errors
        error_popup.setWindowTitle("Error")  # Title of the popup
        error_popup.setText(f"Invalid input for airport {airport}")  # Error message text
        error_popup.setInformativeText("Please input a positive integer")  # Additional information
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
    window = AirportInputWindow()
    window.show()
    sys.exit(app.exec_())

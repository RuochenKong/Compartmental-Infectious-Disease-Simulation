import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox, QLabel
from PyQt5.QtCore import Qt

AIRPORTS = [line.split(',')[0] for line in open('../airport_data_process/exist_airport_GeoId.csv').readlines()][1:]
AIRPORTS.sort()

AIRPORTS_INFO = {}
tmp_df = pd.read_csv('../src_data/airports_geoinfo.csv')
for k,v in zip(tmp_df['iata_code'], tmp_df['name']):
    AIRPORTS_INFO[k] = v

class DynamicInputApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create the main vertical layout
        self.main_layout = QVBoxLayout()

        # A separate layout to hold the input rows
        self.input_layout = QVBoxLayout()
        self.main_layout.addLayout(self.input_layout)

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

        # Description
        description_label = QLabel("Select an airport")
        description_label.setFixedWidth(300)  # Set a fixed width for readability
        description_label.setAlignment(Qt.AlignRight)  # Align text to the right
        description_label.setStyleSheet("color: blue;")  # Set text color to red

        # Create a label and input line
        combo_box = QComboBox(self)
        combo_box.addItems(AIRPORTS)
        input_line = QLineEdit()

        # update description
        combo_box.currentIndexChanged.connect(
            lambda: self.update_description(combo_box, description_label)
        )

        # Create a "Remove Line" button
        remove_button = QPushButton("-")
        remove_button.setFixedWidth(20)
        remove_button.clicked.connect(lambda: self.remove_input_row(row_layout))

        # Add the label and input line to the horizontal layout
        row_layout.addWidget(description_label)
        row_layout.addWidget(combo_box)
        row_layout.addWidget(input_line)
        row_layout.addWidget(remove_button)

        # Add the horizontal layout to the main vertical layout
        self.input_layout.addLayout(row_layout)

    def remove_input_row(self, row_layout):
        # Remove all widgets in the given row layout
        while row_layout.count():
            widget = row_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        # Remove the row layout itself from the parent layout
        self.input_layout.removeItem(row_layout)

    def update_description(self, combo_box, description_label):

        # Update the description label based on the selected option
        selected_option = combo_box.currentText()
        description_label.setText(AIRPORTS_INFO.get(selected_option, "Error"))
        description_label.setStyleSheet("color: black;")  # Set text color to red


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynamicInputApp()
    window.show()
    sys.exit(app.exec_())

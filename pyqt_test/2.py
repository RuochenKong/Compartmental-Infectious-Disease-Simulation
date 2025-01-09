import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox

class DynamicInputApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Main vertical layout for the entire window
        self.main_layout = QVBoxLayout()

        # A separate layout to hold the input rows
        self.input_layout = QVBoxLayout()
        self.main_layout.addLayout(self.input_layout)

        # Create the "Add Input Line" button
        self.button = QPushButton("Add Input Line")
        self.button.clicked.connect(self.add_input_row)

        # Add the button to the bottom of the main layout
        self.main_layout.addWidget(self.button)

        # Set the layout for the main window
        self.setLayout(self.main_layout)

        self.setWindowTitle("Dynamic Input Rows with Descriptions")
        self.setGeometry(100, 100, 600, 300)

    def add_input_row(self):
        # Create a horizontal layout for the new row
        row_layout = QHBoxLayout()

        # Create a combo box with predefined options
        combo_box = QComboBox()
        combo_box.addItems(["Option 1", "Option 2", "Option 3"])

        # Create a QLabel to show the description for the selected option
        description_label = QLabel("Select an option")
        description_label.setFixedWidth(200)  # Set a fixed width for readability

        # Update the description label whenever the combo box selection changes
        combo_box.currentIndexChanged.connect(
            lambda: self.update_description(combo_box, description_label)
        )

        # Create an input line
        input_line = QLineEdit()

        # Create a "Remove Line" button
        remove_button = QPushButton("Remove Line")
        remove_button.clicked.connect(lambda: self.remove_input_row(row_layout))

        # Add widgets to the horizontal layout
        row_layout.addWidget(combo_box)
        row_layout.addWidget(description_label)
        row_layout.addWidget(input_line)
        row_layout.addWidget(remove_button)

        # Add the horizontal layout to the input layout (above the main button)
        self.input_layout.addLayout(row_layout)

    def update_description(self, combo_box, description_label):
        # Map each combo box option to a description
        descriptions = {
            "Option 1": "Description for Option 1",
            "Option 2": "Description for Option 2",
            "Option 3": "Description for Option 3",
        }

        # Update the description label based on the selected option
        selected_option = combo_box.currentText()
        description_label.setText(descriptions.get(selected_option, "No description"))

    def remove_input_row(self, row_layout):
        # Remove all widgets in the given row layout
        while row_layout.count():
            widget = row_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        # Remove the row layout itself from the parent layout
        self.input_layout.removeItem(row_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynamicInputApp()
    window.show()
    sys.exit(app.exec_())

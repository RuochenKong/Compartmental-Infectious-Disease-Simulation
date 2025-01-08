import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QLabel

class SelectionBoxDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selection Box Example")
        self.setGeometry(100, 100, 300, 200)

        self.initUI()

    def initUI(self):
        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Label to display selection
        self.label = QLabel("Select an option from the box", self)
        layout.addWidget(self.label)

        # ComboBox for selection
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        layout.addWidget(self.combo_box)

        # Connect selection change signal to the event handler
        self.combo_box.currentIndexChanged.connect(self.on_selection_change)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def on_selection_change(self):
        selected_text = self.combo_box.currentText()
        self.label.setText(f"Selected: {selected_text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SelectionBoxDemo()
    demo.show()
    sys.exit(app.exec_())

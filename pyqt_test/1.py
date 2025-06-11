from PyQt5.QtWidgets import QApplication, QWidget, QCheckBox, QVBoxLayout

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Checkbox Example")

        # Create the checkboxes
        self.checkbox1 = QCheckBox("Show another checkbox", self)
        self.checkbox2 = QCheckBox("Hidden checkbox", self)
        self.checkbox2.setVisible(False)  # Initially hide the second checkbox

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.checkbox1)
        layout.addWidget(self.checkbox2)
        self.setLayout(layout)

        # Connect signal
        self.checkbox1.stateChanged.connect(self.toggle_checkbox2)

    def toggle_checkbox2(self, state):
        """Toggles visibility of the second checkbox based on the first checkbox's state."""
        if state == 2:  # 2 corresponds to checked
            self.checkbox2.setVisible(True)
        else:
            self.checkbox2.setVisible(False)

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()
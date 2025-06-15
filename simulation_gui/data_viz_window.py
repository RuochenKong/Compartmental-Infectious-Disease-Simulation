import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QProgressBar, QMessageBox, QTextEdit, QFileDialog, QLabel, QSpinBox, QDesktopWidget
)
from PyQt5.QtCore import QProcess
import subprocess
import os


VIZPARAMS = {'Simulate data folder': '-data_dir',
             'Simulation id': '-simu_id',
             'Figure output folder': '-figure_dir'}

class DataVizWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Vizualization")
        self.setGeometry(100, 100, 600, 200)

        self.process = QProcess(self)
        self.process.finished.connect(self.on_finished)
        self.process.readyReadStandardOutput.connect(self.on_stdout)
        self.process.readyReadStandardError.connect(self.on_stderr)

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.data_viz_params = {'-data_dir':None, '-simu_id':None, '-figure_dir':None}

        self.add_folder_select_row('Simulate data folder')
        self.simu_id_input = self.add_integer_input()
        self.add_folder_select_row('Figure output folder')

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)

        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.output_area.setFixedHeight(50)

        self.start_button = QPushButton("Generate Figures")
        self.start_button.clicked.connect(self.run_figure_generation)

        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.output_area)

        self.viz_button = QPushButton("Visualization")
        self.viz_button.clicked.connect(self.run_viz)

        self.layout.addWidget(self.viz_button)

        self.setLayout(self.layout)
        self.center()

    def center(self):
        # Get the geometry of the primary screen
        screen_geometry = QDesktopWidget().availableGeometry()
        window_geometry = self.frameGeometry()

        # Calculate the center point of the screen
        screen_center = screen_geometry.center()
        screen_center.setY(max(100, screen_center.y() + 100))

        # Move the window's center to the screen's center
        window_geometry.moveCenter(screen_center)

        # Move the top-left corner of the window to align with the new center
        self.move(window_geometry.topLeft())

    def add_folder_select_row(self, text):
        row_layout = QHBoxLayout()

        description = QLabel(text)
        description.setFixedWidth(200)

        folder_button = QPushButton("Select Folder")
        folder_button.setFixedWidth(150)

        folder_display = QLabel("No folder selected.")
        folder_button.clicked.connect(
            lambda _, lbl=folder_display, param=VIZPARAMS[text]: self.select_folder(lbl, param)
        )


        row_layout.addWidget(description)
        row_layout.addWidget(folder_button)
        row_layout.addWidget(folder_display)

        self.layout.addLayout(row_layout)

    def select_folder(self, folder_display, param_label):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            "",  # start directory
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.data_viz_params[param_label] = folder
            folder_display.setText(f"{folder}")
        else:
            folder_display.setText("No folder selected.")


    def add_integer_input(self):
        row_layout = QHBoxLayout()

        description = QLabel('Simulation id')
        description.setFixedWidth(200)

        input_line = QSpinBox(self)
        input_line.setMinimum(0)
        input_line.setValue(0)

        row_layout.addWidget(description)
        row_layout.addWidget(input_line)

        self.layout.addLayout(row_layout)

        return input_line

    def run_figure_generation(self):
        for k,v in self.data_viz_params.items():
            if k == '-simu_id':
                self.data_viz_params[k] = self.simu_id_input.value()
                continue
            if v is None:
                msg = 'Simulate data folder' if 'data' in k else 'Figure output folder'
                msg += ' not specified'
                self.show_missing_input_error(msg)
                return

        self.progress_bar.setMaximum(0)
        self.start_button.setEnabled(False)
        self.output_area.clear()

        self.process.setProgram(sys.executable)
        self.process.setArguments(["../data_viz/generate_figures.py", "-data_dir", self.data_viz_params["-data_dir"],
                                   "-simu_id", f"{self.data_viz_params["-simu_id"]}", "-figure_dir",self.data_viz_params["-figure_dir"]])
        self.process.start()

    def run_viz(self):
        if self.data_viz_params["-figure_dir"] is None:
            self.show_missing_input_error('Figure output folder not specified.')
            return
        self.data_viz_params['-simu_id'] = self.simu_id_input.value()
        viz_path = os.path.join(self.data_viz_params["-figure_dir"], f"simu_{self.data_viz_params["-simu_id"]}")
        if not os.path.exists(viz_path):
            self.show_missing_input_error('Click "Generate Figures" first.')
            return
        subprocess.Popen(["python", "../data_viz/figure_display.py", viz_path])

    def show_missing_input_error(self, main_text):
        error_popup = QMessageBox(self)
        error_popup.setIcon(QMessageBox.Critical)  # Critical icon for errors
        error_popup.setWindowTitle("Error")  # Title of the popup
        error_popup.setText(main_text)  # Error message text
        error_popup.setStandardButtons(QMessageBox.Ok)  # OK button to close the popup

        # Move to center of the screen
        screen_geometry = QDesktopWidget().availableGeometry()
        box_geometry = error_popup.frameGeometry()
        center_point = screen_geometry.center()
        box_geometry.moveCenter(center_point)
        error_popup.move(box_geometry.topLeft())

        error_popup.exec_()  # Show the popup

    def on_stdout(self):
        output = self.process.readAllStandardOutput().data().decode()
        self.output_area.append(f"<b>Output:</b> {output.strip()}")

    def on_stderr(self):
        error_output = self.process.readAllStandardError().data().decode()
        self.output_area.append(f"<span style='color:red'><b>Error:</b> {error_output.strip()}</span>")
        # Also show popup immediately if there's stderr
        QMessageBox.critical(self, "Script Error", error_output.strip())

    def on_finished(self, exit_code, exit_status):
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(1)
        self.start_button.setEnabled(True)

        if exit_code != 0:
            QMessageBox.critical(self, "Failure", f"Script exited with code {exit_code}.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataVizWindow()
    window.show()
    sys.exit(app.exec_())

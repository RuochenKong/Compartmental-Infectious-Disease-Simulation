import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,QHBoxLayout, QSpinBox
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import pandas as pd

class ShapefileViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000,1000)
        self.setWindowTitle("Disease Spreading Map")
        self.shapefile_path = "../src_data/us_county/us_county.shp"
        self.display_day = 0
        self.ax = None
        self.gdf = None
        self.original_xlim = None
        self.original_ylim = None

        self.simu_out_df = pd.read_csv('../sample_output/simu_2.csv')
        self.simu_out_df['county'] = self.simu_out_df['cbg'].apply(lambda x: str(x)[:5])

        # Main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # Layout
        self.layout = QVBoxLayout(self.main_widget)

        # Plot canvas
        self.canvas = FigureCanvas(plt.figure())
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

        self.add_button_row()
        self.display_original()
        self.canvas.figure.tight_layout()

        # Load shapefile button
        # self.load_button = QPushButton("Load Shapefile")
        # self.load_button.clicked.connect(self.load_shapefile)
        # layout.addWidget(self.load_button)

    def add_button_row(self):
        row_layout = QHBoxLayout()

        zoom_out_button = QPushButton("View Full Map")
        zoom_out_button.clicked.connect(self.display_zoom_out)
        zoom_in_button = QPushButton("View Mainland")
        zoom_in_button.clicked.connect(self.display_zoom_in)
        next_day_button = QPushButton(">")
        next_day_button.setFixedWidth(50)

        certain_day_button = QSpinBox(self)
        certain_day_button.setMinimum(0)
        certain_day_button.setMaximum(90)
        certain_day_button.setFixedWidth(70)
        certain_day_button.setValue(0)
        next_day_button.clicked.connect(lambda: self.display_next_day(certain_day_button))
        certain_day_button.valueChanged.connect(self.display_certain_day)

        last_day_button = QPushButton("<")
        last_day_button.setFixedWidth(50)
        last_day_button.clicked.connect(lambda: self.display_last_day(certain_day_button))

        row_layout.addWidget(last_day_button)
        row_layout.addWidget(certain_day_button)
        row_layout.addWidget(next_day_button)
        row_layout.addWidget(zoom_in_button)
        row_layout.addWidget(zoom_out_button)

        self.layout.addLayout(row_layout)

    def display_zoom_out(self):
        # Ensure an axis exists
        if self.ax is not None:
            # Get current axis limits
            xlim = self.original_xlim
            ylim = self.original_ylim

            # Set new limits
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)

            # Redraw the canvas
            self.canvas.draw()

    def display_zoom_in(self):
        # Ensure an axis exists
        if self.ax is not None:
            # Get current axis limits
            xlim = self.original_xlim

            # Set new limits
            new_xlim = [xlim[0],  xlim[0]+150]
            self.ax.set_xlim(new_xlim)

            # Redraw the canvas
            self.canvas.draw()

    def display_the_day(self):

        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()

        self.ax.cla()
        simu_day_df = self.simu_out_df[self.simu_out_df['day'] <= self.display_day].groupby('county')[['infectious', 'recovered']].sum()
        simu_day_df['current infectious'] = simu_day_df['infectious'] - simu_day_df['recovered']

        display_df = self.gdf.merge(simu_day_df, left_on='GEO_ID', right_on='county', how = 'left')
        display_df = display_df.fillna(0)
        display_df.plot(column='infectious', cmap='Blues',edgecolor='black', linewidth=0.1, ax=self.ax, legend=False, vmin = 0, vmax = 100)


        print(self.display_day)
        print(display_df['current infectious'].sum())
        print(display_df['infectious'].sum())

        self.ax.set_xlim(current_xlim)
        self.ax.set_ylim(current_ylim)

        self.ax.set_title(f"Day {self.display_day}")

        # self.canvas.draw()

    def display_certain_day(self, value):
        self.display_day = value
        if value == 0:
            self.display_original()
        elif self.ax is not None:
            self.display_the_day()

    def display_next_day(self,certain_day_button):
        if self.display_day == 90:
            return
        if self.ax is not None:
            self.display_day += 1
            self.display_the_day()
            certain_day_button.setValue(self.display_day)

    def display_last_day(self,certain_day_button):
        if self.display_day == 1:
            return
        if self.ax is not None:
            self.display_day -= 1
            self.display_the_day()
            certain_day_button.setValue(self.display_day)


    def display_original(self):

        try:
            # Load shapefile using geopandas
            self.gdf = gpd.read_file(self.shapefile_path)

            # Plot shapefile
            self.ax = self.canvas.figure.add_subplot(111)
            self.ax.clear()

            self.gdf.plot(ax=self.ax, facecolor='white', edgecolor='black', linewidth = 0.1)

            # Disable grid lines
            # self.ax.axis('off')
            # self.ax.grid(True)


            self.original_xlim = self.ax.get_xlim()
            self.original_ylim = self.ax.get_ylim()

            xlim = self.original_xlim
            ylim = self.original_ylim

            new_xlim = [xlim[0],  xlim[0]+150]
            self.ax.set_xlim(new_xlim)

            area = Rectangle(
                (xlim[0], ylim[0]),              # Bottom-left corner
                xlim[1] - xlim[0],              # Width
                ylim[1] - ylim[0],
                linewidth=1,
                edgecolor='red',
                facecolor='none',
                linestyle='-.'
            )

            # Add the rectangle to the plot
            self.ax.add_patch(area)

            self.ax.set_title("Initial Map")
            # Hide the outer spines
#             for spine in self.ax.spines.values():
#                 spine.set_visible(True)

            self.canvas.draw()

        except Exception as e:
            print(f"Error loading shapefile: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ShapefileViewer()
    viewer.show()
    sys.exit(app.exec_())

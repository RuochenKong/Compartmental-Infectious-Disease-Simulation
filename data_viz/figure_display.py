import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
import os
import sys
from PIL import Image

def load_images_from_folder(folder):
    img_fns = [os.path.join(folder, 'Day%d.png'%day) for day in range(len(os.listdir(folder)))]
    images = []
    for img_fn in img_fns:
        try:
            img = Image.open(img_fn)
            images.append(np.array(img))
        except Exception as e:
            print(f"Error loading {img_fn.split('/')[-1]}: {e}")
    return images

# Path to your image folder
try:
    image_folder = sys.argv[1]
except:
    print('Missing argument on figure folder.')
    exit(1)

# Load images
image_list = load_images_from_folder(image_folder)

if not image_list:
    print("No images found in the specified folder.")
else:
    # Set up the figure and axes
    fig, ax = plt.subplots(figsize=(10,10))
    plt.subplots_adjust(bottom=0.25)
    plt.tight_layout()
    current_image_index = 0
    im = ax.imshow(image_list[current_image_index])

    # Create slider axis
    ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03])
    ax.axis('off')
    # Create slider
    slider = Slider(ax_slider, "Day", 0, len(image_list) - 1, valinit=current_image_index, valstep=1)

    # Function to update the image
    def update(val):
        global current_image_index
        current_image_index = int(slider.val)
        im.set_data(image_list[current_image_index])
        fig.canvas.draw_idle()

    # Connect slider to update function
    slider.on_changed(update)

    plt.show()
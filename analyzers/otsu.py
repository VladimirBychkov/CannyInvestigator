import PySimpleGUI as sg
import numpy as np
from skimage.filters import threshold_otsu
from PIL import Image


def get_layout():
    layout = [
        [sg.Frame(layout=[
            [
                sg.Checkbox("Red", default=True, key='-OTSU RED CHANNEL-'),
                sg.Checkbox("Green", default=True, key='-OTSU GREEN CHANNEL-'),
                sg.Checkbox("Blue", default=True, key='-OTSU BLUE CHANNEL-'),
            ]
        ], title="Otsu Channels")],
    ]

    return layout


def process_image(pil_image, values):
    img = np.array(pil_image)
    selected_channels = [values["-OTSU RED CHANNEL-"], values["-OTSU GREEN CHANNEL-"], values["-OTSU BLUE CHANNEL-"]]

    def mask_channels(img, selected_channels):
        img[..., np.where(np.invert(selected_channels))] = 0

    if np.where(selected_channels)[0].size == 1:
        threshold_global_otsu = threshold_otsu(img[..., np.where(selected_channels)[0][0]])
        global_otsu = img[..., np.where(selected_channels)[0][0]] >= threshold_global_otsu
        ret_img = Image.fromarray(255 * np.asarray(global_otsu, dtype=np.uint8))
    else:
        ret_img = pil_image

    return ret_img

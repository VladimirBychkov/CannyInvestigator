import PySimpleGUI as sg
import numpy as np
from skimage import feature
from PIL import Image


def get_layout():
    layout = [
        [
            sg.Checkbox("Apply Canny", default=False, key="-APPLY CANNY-"),
            sg.Checkbox("Overlay with Image", default=False, key="-OVERLAY WITH IMAGE-"),
        ],
        [sg.Frame(layout=[
            [
                sg.Checkbox("Red", default=True, key='-RED CHANNEL-'),
                sg.Checkbox("Green", default=True, key='-GREEN CHANNEL-'),
                sg.Checkbox("Blue", default=True, key='-BLUE CHANNEL-'),
            ]
        ], title="Canny Channels")],
        [sg.Frame(layout=[
            [
                sg.Text("Blur"),
                sg.Slider((1, 15), 1, 1, orientation="h", size=(40, 15), key="-CANNY BLUR-"),
            ],
            [
                sg.Text("Low"),
                sg.Slider((0, 20), 10, 1, orientation="h", size=(19, 15), key="-CANNY LOW-"),
                sg.Text("High"),
                sg.Slider((0, 20), 10, 1, orientation="h", size=(19, 15), key="-CANNY HIGH-"),
            ]
        ], title="Canny Parameters")],
    ]

    return layout


def process_image(pil_image, values):
    img = np.array(pil_image)
    selected_channels = [values["-RED CHANNEL-"], values["-GREEN CHANNEL-"], values["-BLUE CHANNEL-"]]

    def mask_channels(img, selected_channels):
        img[..., np.where(np.invert(selected_channels))] = 0

    if values["-APPLY CANNY-"]:
        if np.where(selected_channels)[0].size == 1 and len(img.shape) == 2:
            selected_img = img.copy()
            selected_img = 255 * np.asarray(feature.canny(selected_img,
                                                          values["-CANNY BLUR-"],
                                                          values["-CANNY LOW-"],
                                                          values["-CANNY HIGH-"]), dtype=np.uint8)
            if values["-OVERLAY WITH IMAGE-"]:
                img[np.where(selected_img)] = 255
            else:
                img = selected_img
        elif np.where(selected_channels)[0].size == 1:
            selected_img = img[..., np.where(selected_channels)[0][0]].copy()
            selected_img = 255 * np.asarray(feature.canny(selected_img,
                                                          values["-CANNY BLUR-"],
                                                          values["-CANNY LOW-"],
                                                          values["-CANNY HIGH-"]), dtype=np.uint8)
            if values["-OVERLAY WITH IMAGE-"]:
                ids = np.where(selected_img)
                img[ids[0], ids[1], :] = 255
            else:
                img[..., np.where(selected_channels)[0][0]] = selected_img
                mask_channels(img, selected_channels)
    else:
        if len(img.shape) == 3:
            mask_channels(img, selected_channels)

    return Image.fromarray(img)

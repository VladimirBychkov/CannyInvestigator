import PySimpleGUI as sg
import numpy as np
from skimage.morphology import disk, diamond, rectangle
from skimage.filters import threshold_otsu, rank
from PIL import Image


def get_layout():
    layout = [
        [sg.Frame(layout=[
            [
                sg.Checkbox("Red", default=True, key='-OTSU RED CHANNEL-'),
                sg.Checkbox("Green", default=True, key='-OTSU GREEN CHANNEL-'),
                sg.Checkbox("Blue", default=True, key='-OTSU BLUE CHANNEL-'),
            ]
        ], title="Channels")],
        [
            sg.Checkbox("Local Otsu", default=False, key="-APPLY LOCAL OTSU-"),
        ],
        [sg.Frame(layout=[
            [
                sg.Text("Size"),
                sg.Slider((1, 150), 1, 1, orientation="h", size=(40, 15), key="-LOCAL OTSU SIZE-"),
            ],
            [
                sg.Text("Local Shape"),
                sg.InputCombo(("Disk", "Rect"), default_value="Disk", enable_events=True, key="-LOCAL OTSU SHAPE-", size=(10, 15)),
            ],
        ], title="Local Otsu Parameter")],
    ]

    return layout


def process_image(pil_image, values):
    img = np.array(pil_image)
    selected_channels = [values["-OTSU RED CHANNEL-"], values["-OTSU GREEN CHANNEL-"], values["-OTSU BLUE CHANNEL-"]]

    if np.where(selected_channels)[0].size == 1 and len(img.shape) == 2:
        if values["-APPLY LOCAL OTSU-"]:
            radius = values["-LOCAL OTSU SIZE-"]
            local_mask = disk(radius) if values["-LOCAL OTSU SHAPE-"] == "Disk" else rectangle(int(radius), int(radius))
            local_otsu = img >= rank.otsu(img, local_mask)
            ret_img = Image.fromarray(255 * np.asarray(local_otsu, dtype=np.uint8))
        else:
            global_otsu = img >= threshold_otsu(img)
            ret_img = Image.fromarray(255 * np.asarray(global_otsu, dtype=np.uint8))
    elif np.where(selected_channels)[0].size == 1:
        if values["-APPLY LOCAL OTSU-"]:
            radius = values["-LOCAL OTSU SIZE-"]
            local_mask = disk(radius) if values["-LOCAL OTSU SHAPE-"] == "Disk" else rectangle(int(radius), int(radius))
            local_otsu = img[..., np.where(selected_channels)[0][0]] >= rank.otsu(img[..., np.where(selected_channels)[0][0]], local_mask)
            ret_img = Image.fromarray(255 * np.asarray(local_otsu, dtype=np.uint8))
        else:
            threshold_global_otsu = threshold_otsu(img[..., np.where(selected_channels)[0][0]])
            global_otsu = img[..., np.where(selected_channels)[0][0]] >= threshold_global_otsu
            ret_img = Image.fromarray(255 * np.asarray(global_otsu, dtype=np.uint8))
    else:
        ret_img = pil_image

    return ret_img

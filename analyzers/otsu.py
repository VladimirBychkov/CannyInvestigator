import PySimpleGUI as sg
import numpy as np
import cv2.cv2 as cv2
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
            sg.Checkbox("Overlay with Image", default=False, key="-OTSU OVERLAY WITH IMAGE-"),
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
            otsu_img = img >= rank.otsu(img, local_mask)
        else:
            otsu_img = img >= threshold_otsu(img)

        otsu_np_img = 255 * np.asarray(otsu_img, dtype=np.uint8)
        if values["-OTSU OVERLAY WITH IMAGE-"]:
            cnts = cv2.findContours(otsu_np_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[0]
            cv2.drawContours(img, cnts, -1, 255, 1)
            otsu_np_img = img
        ret_img = Image.fromarray(otsu_np_img)

    elif np.where(selected_channels)[0].size == 1:
        if values["-APPLY LOCAL OTSU-"]:
            radius = values["-LOCAL OTSU SIZE-"]
            local_mask = disk(radius) if values["-LOCAL OTSU SHAPE-"] == "Disk" else rectangle(int(radius), int(radius))
            otsu_img = img[..., np.where(selected_channels)[0][0]] >= rank.otsu(img[..., np.where(selected_channels)[0][0]], local_mask)
        else:
            threshold_global_otsu = threshold_otsu(img[..., np.where(selected_channels)[0][0]])
            otsu_img = img[..., np.where(selected_channels)[0][0]] >= threshold_global_otsu

        otsu_np_img = 255 * np.asarray(otsu_img, dtype=np.uint8)
        if values["-OTSU OVERLAY WITH IMAGE-"]:
            cnts = cv2.findContours(otsu_np_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[0]
            cv2.drawContours(img, cnts, -1, 255, 1)
            otsu_np_img = img
        ret_img = Image.fromarray(otsu_np_img)

    else:
        ret_img = pil_image

    return ret_img

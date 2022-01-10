import PySimpleGUI as sg
import cv2


def get_layout():
    layout = [
        [sg.Radio("no filters", "Radio", True, size=(10, 1), key="-NO FILTERS-")],
        [
            sg.Radio("threshold", "Radio", size=(10, 1), key="-THRESH-"),
            sg.Slider((0, 255), 128, 1, orientation="h", size=(40, 15), key="-THRESH SLIDER-"),
        ],
        [
            sg.Radio("canny", "Radio", size=(10, 1), key="-CANNY-"),
            sg.Slider((0, 255), 128, 1, orientation="h", size=(20, 15), key="-CANNY SLIDER A-"),
            sg.Slider((0, 255), 128, 1, orientation="h", size=(20, 15), key="-CANNY SLIDER B-"),
        ],
        [
            sg.Radio("blur", "Radio", size=(10, 1), key="-BLUR-"),
            sg.Slider((1, 11), 1, 1, orientation="h", size=(40, 15), key="-BLUR SLIDER-"),
        ],
        [
            sg.Radio("hue", "Radio", size=(10, 1), key="-HUE-"),
            sg.Slider((0, 225), 0, 1, orientation="h", size=(40, 15), key="-HUE SLIDER-"),
        ],
        [
            sg.Radio("enhance", "Radio", size=(10, 1), key="-ENHANCE-"),
            sg.Slider((1, 255), 128, 1, orientation="h", size=(40, 15), key="-ENHANCE SLIDER-"),
        ],
    ]

    return layout


def process_frame(frame, values):
    if values["-THRESH-"]:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)[:, :, 0]
        frame = cv2.threshold(frame, values["-THRESH SLIDER-"], 255, cv2.THRESH_BINARY)[1]

    elif values["-CANNY-"]:
        frame = cv2.Canny(frame, values["-CANNY SLIDER A-"], values["-CANNY SLIDER B-"])

    elif values["-BLUR-"]:
        frame = cv2.GaussianBlur(frame, (21, 21), values["-BLUR SLIDER-"])

    elif values["-HUE-"]:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame[:, :, 0] += int(values["-HUE SLIDER-"])
        frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

    elif values["-ENHANCE-"]:
        enh_val = values["-ENHANCE SLIDER-"] / 40
        clahe = cv2.createCLAHE(clipLimit=enh_val, tileGridSize=(8, 8))
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    return frame

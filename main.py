import os
import PySimpleGUI as sg
import cv2.cv2 as cv2
import numpy as np
from skimage import feature
from PIL import Image, ImageTk


DEFAULT_FOLDER = r"D:\Downloads"


def get_layout():
    file_list_column = [
        [
            sg.Text("Image Folder"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-FILE LIST-")
        ],
    ]

    image_viewer_column = [
        [sg.Text("Choose an image from list on left:")],
        [sg.Text(size=(40, 1), key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
    ]

    layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(image_viewer_column),
        ]
    ]

    return layout


def get_file_names(folder):
    try:
        file_list = os.listdir(folder)
    except:
        file_list = []

    file_names = [f for f in file_list
                  if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith((".png", ".gif", ".bmp"))]

    return file_names


def get_opencv_layout():
    image_tab_layout = [
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
        ], title="Channels")],
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

    video_tab_layout = [
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

    right_column = [
        [sg.Text("Image Folder")],
        [
            sg.In(default_text=DEFAULT_FOLDER, size=(50, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(values=get_file_names(DEFAULT_FOLDER), enable_events=True, size=(60, 15), key="-FILE LIST-")
        ],
        [
            sg.TabGroup(layout=[
                [
                    sg.Tab("Image Viewer", image_tab_layout, key="-IMAGE VIEWER TAB-"),
                    sg.Tab("Video Viewer", video_tab_layout, key="-VIDEO VIEWER TAB-"),
                ]
            ], enable_events=True, key="-TAB GROUP-")
        ],
        [
            sg.HSeparator()
        ],
        [
            sg.Button("Exit", size=(10, 1))
        ],
    ]

    image_viewer_column = [
        [sg.Text("Choose an image from list on left:")],
        [sg.Text(size=(80, 1), key="-TOUT-")],
        [sg.Image(size=(512, 512), key="-IMAGE-")],
    ]

    layout = [
        [
            sg.Column(right_column),
            sg.VSeperator(),
            sg.Column(image_viewer_column),
        ]
    ]

    return layout


def run_app():
    layout = get_opencv_layout()

    window = sg.Window("Canny Investigator", layout)

    cap = cv2.VideoCapture(0)
    current_pil_image = None

    while True:
        event, values = window.read(timeout=20)

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if values["-TAB GROUP-"] == "-VIDEO VIEWER TAB-":
            ret, frame = cap.read()

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

            img_bytes = cv2.imencode(".png", frame)[1].tobytes()

            window["-IMAGE-"].update(data=img_bytes)

        elif values["-TAB GROUP-"] == "-IMAGE VIEWER TAB-":
            selected_channels = [values["-RED CHANNEL-"], values["-GREEN CHANNEL-"], values["-BLUE CHANNEL-"]]

            if event == "-FOLDER-":
                folder = values["-FOLDER-"]
                file_names = os.listdir(folder)

                window["-FILE LIST-"].update(file_names)

            elif event == "-FILE LIST-":
                try:
                    filename = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])

                    current_pil_image = Image.open(filename)
                    img = np.array(current_pil_image)

                    window["-TOUT-"].update(filename)

                    if len(img.shape) == 3:
                        for channel, is_selected in enumerate(selected_channels):
                            if not is_selected:
                                img[:, :, channel] = 0
                        pil_image = Image.fromarray(img)
                    else:
                        pil_image = current_pil_image

                    window["-IMAGE-"].update(data=ImageTk.PhotoImage(pil_image))
                except:
                    pass

            if values["-APPLY CANNY-"]:
                try:
                    if np.where(selected_channels)[0].size == 1:
                        pil_image = current_pil_image
                        img = np.array(pil_image)
                        if len(img.shape) == 3:
                            temp_img = img[..., np.where(selected_channels)[0][0]].copy()

                            temp_img = np.asarray(feature.canny(temp_img,
                                                                values["-CANNY BLUR-"],
                                                                values["-CANNY LOW-"],
                                                                values["-CANNY HIGH-"]), dtype=np.uint8)
                            temp_img[np.where(temp_img)] = 255

                            if values["-OVERLAY WITH IMAGE-"]:
                                ids = np.where(temp_img)
                                img[ids[0], ids[1], :] = 255
                            else:
                                img[..., np.where(selected_channels)[0][0]] = temp_img
                                for channel, is_selected in enumerate(selected_channels):
                                    if not is_selected:
                                        img[..., channel] = 0

                            pil_image = Image.fromarray(img)

                            window["-IMAGE-"].update(data=ImageTk.PhotoImage(pil_image))
                except:
                    pass

            else:
                try:
                    pil_image = current_pil_image
                    img = np.array(current_pil_image)
                    if len(img.shape) == 3:
                        for channel, is_selected in enumerate(selected_channels):
                            if not is_selected:
                                img[:, :, channel] = 0
                        pil_image = Image.fromarray(img)

                    if pil_image:
                        window["-IMAGE-"].update(data=ImageTk.PhotoImage(pil_image))
                except:
                    pass

    window.close()


if __name__ == '__main__':
    run_app()

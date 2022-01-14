import os
import PySimpleGUI as sg
import cv2.cv2 as cv2
import numpy as np
from PIL import Image, ImageTk

import analyzers.video_fun
import analyzers.canny
import analyzers.otsu


DEFAULT_FOLDER = r"D:\Downloads"


def get_file_names(folder):
    try:
        file_list = os.listdir(folder)
    except:
        file_list = []

    file_names = [f for f in file_list
                  if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith((".png", ".gif", ".bmp"))]

    return file_names


def get_layout():
    menu_def = [
        ['File', ['Open', 'Save', 'Exit', 'Properties']],
        ['Analyze Image', ['Viewer', 'Canny Edge Detection', 'Otsu', 'Video Fun', 'Paste', ['Special', 'Normal', ], 'Undo'], ],
        ['Help', 'About...'],
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
            sg.Column([[]], visible=True, key="-DEFAULT LAYOUT-"),
            sg.Column(analyzers.canny.get_layout(), visible=False, key="-CANNY LAYOUT-"),
            sg.Column(analyzers.otsu.get_layout(), visible=False, key="-OTSU LAYOUT-"),
            sg.Column(analyzers.video_fun.get_layout(), visible=False, key="-VIDEO LAYOUT-"),
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
        [sg.Menu(menu_def, tearoff=False)],
        [
            sg.Column(right_column),
            sg.VSeperator(),
            sg.Column(image_viewer_column),
        ]
    ]

    return layout


def run_app():
    layout = get_layout()

    window = sg.Window("Canny Investigator", layout)

    cap = cv2.VideoCapture(0)
    current_pil_image = None
    chosen_layout = "Viewer"

    while True:
        event, values = window.read(timeout=20)

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event == "-FOLDER-":
            file_names = os.listdir(values["-FOLDER-"])
            window["-FILE LIST-"].update(file_names)

        if event == "-FILE LIST-":
            filename = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])

            current_pil_image = Image.open(filename)

            if np.max(current_pil_image.size) > 1024:
                current_pil_image.thumbnail((1024, 1024), Image.ANTIALIAS)

            window["-TOUT-"].update(filename)
            window["-IMAGE-"].update(data=ImageTk.PhotoImage(current_pil_image))

        if event == "Viewer":
            chosen_layout = event
            window["-CANNY LAYOUT-"].update(visible=False)
            window["-OTSU LAYOUT-"].update(visible=False)
            window["-VIDEO LAYOUT-"].update(visible=False)
            window["-DEFAULT LAYOUT-"].update(visible=True)

        if event == "Video Fun":
            chosen_layout = event
            window["-DEFAULT LAYOUT-"].update(visible=False)
            window["-CANNY LAYOUT-"].update(visible=False)
            window["-OTSU LAYOUT-"].update(visible=False)
            window["-VIDEO LAYOUT-"].update(visible=True)

        elif chosen_layout == "Video Fun":
            ret, frame = cap.read()

            frame = analyzers.video_fun.process_frame(frame, values)

            img_bytes = cv2.imencode(".png", frame)[1].tobytes()
            current_pil_image = Image.fromarray(frame)

            window["-IMAGE-"].update(data=img_bytes)

        if event == "Canny Edge Detection":
            chosen_layout = "Canny Edge Detection"
            window["-DEFAULT LAYOUT-"].update(visible=False)
            window["-VIDEO LAYOUT-"].update(visible=False)
            window["-OTSU LAYOUT-"].update(visible=False)
            window["-CANNY LAYOUT-"].update(visible=True)

        elif chosen_layout == "Canny Edge Detection":
            try:
                pil_image = analyzers.canny.process_image(current_pil_image, values)
                window["-IMAGE-"].update(data=ImageTk.PhotoImage(pil_image))
            except:
                pass

        if event == "Otsu":
            chosen_layout = "Otsu"
            window["-DEFAULT LAYOUT-"].update(visible=False)
            window["-VIDEO LAYOUT-"].update(visible=False)
            window["-CANNY LAYOUT-"].update(visible=False)
            window["-OTSU LAYOUT-"].update(visible=True)

        elif chosen_layout == "Otsu":
            try:
                pil_image = analyzers.otsu.process_image(current_pil_image, values)
                window["-IMAGE-"].update(data=ImageTk.PhotoImage(pil_image))
            except:
                pass

    window.close()


if __name__ == '__main__':
    run_app()

import os
import PySimpleGUI as sg
import cv2


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


def get_opencv_layout():
    right_column = [[
            sg.Text("Image Folder"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-FILE LIST-")
        ],
        [sg.Radio("None", "Radio", True, size=(10, 1), key="-NONE-")],
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
        [sg.Button("Exit", size=(10, 1))],
    ]
    image_viewer_column = [
        [sg.Text("Choose an image from list on left:")],
        [sg.Text(size=(40, 1), key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
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

    while True:
        event, values = window.read(timeout=20)

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if not values["-NONE-"]:
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
        else:
            if event == "-FOLDER-":
                folder = values["-FOLDER-"]
                try:
                    file_list = os.listdir(folder)
                except:
                    file_list = []

                file_names = [f for f in file_list
                              if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith((".png", ".gif"))]
                window["-FILE LIST-"].update(file_names)

            elif event == "-FILE LIST-" and values["-NONE-"]:
                try:
                    filename = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])
                    window["-TOUT-"].update(filename)
                    window["-IMAGE-"].update(filename=filename)
                except:
                    pass

    window.close()


if __name__ == '__main__':
    run_app()

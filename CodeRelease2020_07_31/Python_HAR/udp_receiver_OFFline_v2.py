import datetime
import logging
import socket
import time
import threading
import tkinter as tk
from PIL import ImageTk, Image
from concurrent.futures.thread import ThreadPoolExecutor

log = logging.getLogger('udp_server')

ip_address = "155.230.15.110"
port_number = "5600"
dt = datetime.datetime.now()
RAW_DATA_FILE = f"data/offline/raw_data_{dt.date()}_{dt.hour}-{dt.minute}-{dt.second}_device"
ACTIVITIES = ["WALKING", "STANDING", "SITTING", "LYING", "RUNNING", "IDLE"]

isStarted = False               # Change when click button: True (start the HAR model), False (not start yet, or Stop)
currentActivity = 5            # current activity: is the index of class_names (initial = 5 "IDLE")


def udp_loop():
    def udp_server(host=ip_address, port=port_number):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((host, port))

        while True:
            (buffer, addr) = s.recvfrom(128 * 1024)
            data = buffer.decode("ascii")
            receive_time = f"{time.time():.3f}"
            device_id = data[0]

            print(data)
            if isStarted:
                # save the sensor data to raw_data file
                if not data == "":
                    with open(f"{RAW_DATA_FILE}{device_id}.txt", "a") as raw_data_file:
                        raw_data_file.write(f"{currentActivity}, {data}")
                        raw_data_file.write("\n")

            # with open(f"{RAW_DATA_FILE}{device_id}.txt", "a") as raw_data:
            #     raw_data.write(f"{receive_time}, {data}\n")
            # yield data


    # FORMAT_CONS = '%(asctime)s %(name)-12s %(levelname)8s\t%(message)s'


    for data in udp_server():
        # print("UDP server up and listening")
        log.debug("%r" % (data,))


"""
********************************************* GUI ********************************************
"""


def on_click_start(_btn):
    global isStarted, RAW_DATA_FILE

    if _btn['text'] == 'Start':
        print("Request action: START")
        isStarted = True

        # update new file name --> for OFF-LiNE data collection
        dt = datetime.datetime.now()
        RAW_DATA_FILE = f"data/offline/raw_data_{dt.date()}_{dt.hour}-{dt.minute}-{dt.second}_device"
        print("+++++++++++++++RAW_DATA_FILE = ", RAW_DATA_FILE)

        # Update GUI
        _btn['text'] = 'Stop'
        _btn['fg'] = 'red'  # why it doesn't update this attribute???

    else:
        print("Request action: STOP")
        isStarted = False
        _btn['text'] = 'Start'
        _btn['fg'] = 'green'


def on_click(_action):
    global currentActivity
    currentActivity = _action

    # Update GUI
    for _act in range(len(ACTIVITIES)):
        list_btns[_act]['fg'] = 'red' if _action == _act else 'black'
    print(list_btns[_action]['text'])


# Create_connections()

with ThreadPoolExecutor(max_workers=2) as executor:
    executor.submit(udp_loop)# Create a Tk ROOT widget (a window with a title bar (there can be ONLY ONE root widget)

    root = tk.Tk()
    root.geometry("330x500")
    root.title("GUI HAR model")
    root['bg'] = 'white'

    # Lab logo
    logo_path1 = "images/iSPL_logo_173x32.gif"
    img1 = ImageTk.PhotoImage(Image.open(logo_path1))
    img_frame1 = tk.Label(root, image=img1, borderwidth=0)
    img_frame1.place(x=5, y=0)

    # TITLE texts
    txt_prediction = tk.Label(root, text="LABELLING TOOL ", font="Helvetica 14 bold", fg='green', bg='ghost white')
    txt_prediction.place(x=73, y=50)

    # ACTIVITIES' BUTTONS
    list_btns = []
    for _act in range(len(ACTIVITIES)):
        list_btns.append(tk.Button(root, height=1, width=10, font="Helvetica 12 bold", bd=3,
                                   text=ACTIVITIES[_act], state='active',
                                   command=lambda arg1=_act: on_click(arg1)))
        list_btns[_act].place(x=110, y=_act * 50 + 90)

    # START BUTTON
    btn_Start = tk.Button(root, height=2, width=10, font="Helvetica 16 bold",
                          text="Start", fg='green', state='active',
                          command=lambda: on_click_start(btn_Start))
    btn_Start.place(x=90, y=400)

    while True:
        root.update()


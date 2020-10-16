import datetime
import logging
import socket
import time
from threading import Thread
from concurrent.futures.thread import ThreadPoolExecutor
import tkinter as tk
from PIL import ImageTk, Image

log = logging.getLogger('udp_server')

ip_address = "155.230.15.110"
port_number = "5500"
dt = datetime.datetime.now()
# RAW_DATA_FILE = f"data/realtime/raw_data_{dt.date()}_{dt.hour}-{dt.minute}-{dt.second}_device"
RAW_DATA_FILE = "data/realtime/raw_data.txt"
ACTIVITIES = ["WALKING", "STANDING", "SITTING", "LYING", "RUNNING", "IDLE"]

isStarted = False               # Change when click button: True (start the HAR model), False (not start yet, or Stop)


"""
********************************************* UDP Connection ********************************************
"""
def udp_loop():
    def udp_server(host=ip_address, port=port_number):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((host, port))
        print(host, port)
        while True:
            (buffer, addr) = s.recvfrom(128 * 1024)
            data = buffer.decode("ascii")
            receive_time = f"{time.time():.3f}"
            device_id = data[0]

            print(data)
            if isStarted == 1:
                # save the sensor data to raw_data file
                if not data == "":
                    with open(RAW_DATA_FILE, "a") as raw_data_file:
                        raw_data_file.write(data)
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
def on_click(_btn):
    global isStarted

    if _btn['text'] == 'Start':
        print("Request action: START")
        isStarted = True

        # Update GUI
        _btn['text'] = 'Stop'
        _btn['fg'] = 'red'      # why it doesn't update this attribute???

    else:
        print("Request action: STOP")
        isStarted = False
        _btn['text'] = 'Start'
        _btn['fg'] = 'green'



with ThreadPoolExecutor(max_workers=2) as executor:
    executor.submit(udp_loop)# Create a Tk ROOT widget (a window with a title bar (there can be ONLY ONE root widget)

    # Create a Tk root widget (a window with a title bar (there can be ONLY ONE root widget)
    root = tk.Tk()
    root.geometry("330x500")
    root.title("GUI HAR model")
    root['bg'] = 'white'

    # Lab logo
    logo_path1 = "images/iSPL_logo_173x32.gif"
    img1 = ImageTk.PhotoImage(Image.open(logo_path1))
    img_frame1 = tk.Label(root, image=img1, borderwidth=0)
    img_frame1.place(x=5, y=0)
    print("img_frame", img_frame1.keys())
    print(img_frame1['borderwidth'])

    # Prediction text
    txt_prediction = tk.Label(root, text="PREDICTION RESULT ", font="Helvetica 14 bold", fg='green')
    txt_prediction.place(x=70, y=80)

    txt_pred_result_var = tk.StringVar()
    txt_pred_result = tk.Button(root, height=2, width=10, font="Helvetica 18 bold", fg='black', bg='white', borderwidth=0,
                                textvariable=txt_pred_result_var)
    txt_pred_result_var.set("WALKING")
    txt_pred_result.place(x=88, y=120)

    # Start button
    btn_Start = tk.Button(root, height=2, width=10, font="Helvetica 16 bold",
                          text="Start", fg='green', state='active',
                          command=lambda: on_click(btn_Start))
                          # command=lambda: threading.Thread(target=on_click(btn_Start)).start())
    btn_Start.place(x=90, y=250)

    while True:
        # Read prediction result
        if isStarted:
            try:
                with open('data/realtime/prediction_result.txt', 'r') as _result_file:
                    _lines = _result_file.readlines()
                    # print("Read predicted result", _lines[-1])
                    txt_pred_result_var.set(_lines[-1])

            except FileNotFoundError as e:
                print("There is not prediction result yet", e)

        # time.sleep(1)
        # root.update_idletasks()
        root.update()

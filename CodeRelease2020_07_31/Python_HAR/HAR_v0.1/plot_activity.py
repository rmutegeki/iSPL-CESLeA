"""
******************************** PLOT ACTIVITY ********************************
- Show the predicted activity
- Localization:
    + Position (x, y)
    + Heading
    + Number of steps
"""

import tkinter as tk
import numpy as np
import time
import math
from PIL import ImageTk, Image

location_data_path = "data/realtime/localization_result.txt"
activity_data_path = "data/realtime/prediction_result.txt"

# Create a Tk root widget (a window with a title bar (there can be ONLY ONE root widget)
root = tk.Tk()
root.geometry("450x350")
root.title("GUI HAR model")
root['bg'] = 'white'

# Lab logo
logo_path1 = "images/iSPL_logo_173x32.gif"
img1 = ImageTk.PhotoImage(Image.open(logo_path1))
img_frame1 = tk.Label(root, image=img1, borderwidth=0)
img_frame1.place(x=5, y=0)
print("img_frame", img_frame1.keys())
print(img_frame1['borderwidth'])


# Create text for results
# Using the StringVar and textvariable fro binding, so later we can update the value of calibration status
labels = ['ACTIVITY: ', 'POSITION: ', 'HEADING: ']
tk_labels = []         # array contains all the tk labels
tk_results = []        # array contains all the tk result
var_results = []       # array contains all the StringVar binding to the textvariable in tk_results
for i in range(len(labels)):
    _label = tk.Label(root, text=labels[i], font="Helvetica 16 bold", bg='white')
    tk_labels.append(_label)
    tk_labels[i].place(x=10, y=45*i + 50)

    _var_txt = tk.StringVar()
    var_results.append(_var_txt)

    _result = tk.Label(root, textvariable=var_results[i], font="Helvetica 16 bold", bg='white')
    tk_results.append(_result)
    tk_results[i].place(x=200, y=45 * i + 50)

    # print(tk_results[i].get())

    var_results.append(tk.StringVar())
    # var_results[i].set(f'IMU {i+1}:  0')

while True:
    # Read prediction result
    try:
        with open(location_data_path, 'r') as _loc_file, \
                open(activity_data_path, 'r') as _act_file:
            _loc_lines = _loc_file.readlines()
            _act_lines = _act_file.readlines()

            x, y, heading, steps = _loc_lines[-1].split(",")
            act = _act_lines[-1]

            var_results[0].set(act)
            var_results[1].set(f'{x}, {y}')
            var_results[2].set(heading)
            var_results[3].set(steps)

    except FileNotFoundError as e:
        print("There is not prediction result yet", e)

    # time.sleep(0.5)
    # root.update_idletasks()
    root.update()

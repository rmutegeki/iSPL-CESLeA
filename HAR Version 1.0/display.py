from __future__ import print_function

import datetime
import time
import tkinter as tk

user_activity = {1: "STANDING", 2: "STANDING"}
user_location = {1: [0.0, 0.0],  2: [0.0, 0.0]}

activity_data = {1: "data/activity1.txt", 2: "data/activity2.txt"}
position_data = {1: "data/position1.txt", 2: "data/position2.txt"}


def draw():
    # Activity
    global text
    f1 = tk.Frame(root, width=100, height=100, relief='solid', bd=0)
    f1.place(x=160, y=60)
    text = tk.Label(f1, text='Activity')
    text.pack()

    # Position
    global text1
    f2 = tk.Frame(root, width=100, height=100, relief='solid', bd=0)
    f2.place(x=160, y=100)
    text1 = tk.Label(f2, text='Position')
    text1.pack()

    # Time
    global text2
    f4 = tk.Frame(root, width=100, height=100, relief='solid', bd=0)
    f4.place(x=160, y=140)
    text2 = tk.Label(f4, text='Time')
    text2.pack()


# Activity
def refresher():
    global text
    try:
        label_file = open(activity_data[1], "r")
        user_activity[1] = label_file.readline()
        label_file = open(activity_data[2], "r")
        user_activity[2] = label_file.readline()
    except FileNotFoundError as e:
        print("Error: ", e)
        # time.sleep(2)

    text.configure(text=f' {user_activity[1]}\t\t  {user_activity[2]}', fg="red", font="Consolas 12 bold")
    root.after(1000, refresher)  # every second...


# Time
def refresher1():
    global text2
    text2.configure(text=f'{datetime.datetime.now().strftime("%Y-%m-%d   %H:%M:%S")}', fg="red", font="Consolas 11 bold")
    root.after(1000, refresher1)  # every second..


# Position
def refresher2():
    global text1
    try:
        position_file = open(position_data[1], "r")
        user_location[1] = position_file.readline().split(',')
        position_file = open(position_data[2], "r")
        user_location[2] = position_file.readline().split(',')
    except FileNotFoundError as e:
        print("Error: ", e)
        time.sleep(2)

    text1.configure(text=f'{user_location[1][0]}, {user_location[1][1]}\t  {user_location[2][0]}, {user_location[2][1]}', fg="blue", font="Consolas 10 bold")
    root.after(500, refresher2)  # Every half a second...


root = tk.Tk()
root.title("Digital Companion Version 1.1")
root.geometry('{}x{}'.format(500, 255))

f0 = tk.Frame(root, width=100, height=100, relief='solid', bd=0)
f0.place(x=170, y=20)
text = tk.Label(f0, text='User 1\t\t\t   User 2', fg="black", font="Verdana 10 bold")
text.pack()

f1 = tk.Frame(root, width=100, height=100, relief='solid', bd=0)
f1.place(x=10, y=60)
text = tk.Label(f1, text='Human Activity:      ', fg="black", font="Verdana 10 bold")
text.pack()

f2 = tk.Frame(root, width=100, height=100, relief='solid', bd=0)
f2.place(x=10, y=100)
text = tk.Label(f2, text='Indoor Position: ', fg="black", font="Verdana 10 bold")
text.pack()

f3 = tk.Frame(root, width=100, height=100, relief='solid', bd=0)
f3.place(x=10, y=140)
text = tk.Label(f3, text='Time: ', fg="black", font="Verdana 10 bold")
text.pack()

f4 = tk.Frame(root, width=100, height=100, relief='solid', bd=0)
f4.place(x=150, y=190)
text = tk.Label(f4, text='ACTIVITY RECOGNITION', fg="black", font="Verdana 10 bold")
text.pack()

draw()
refresher()
refresher1()
refresher2()
root.mainloop()
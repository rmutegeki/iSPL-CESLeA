"""
************************************* PLOT LOCATION*************************************
- Plot the localization result
"""

import matplotlib.animation as animation
import matplotlib.pyplot as plt


location_data_path = "data/realtime/localization_result.txt"

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)


def get_position_data(file):
    user_data = open(file, "r").read()
    data_array = user_data.split("\n")
    xar = []
    yar = []
    for line in data_array:
        if len(line) > 1:
            x, y, heading, steps = line.split(",")
            xar.append(float(x))
            yar.append(float(y))
    return xar, yar


def animate(i):

    xar1, yar1 = [], []
    try:
        xar1, yar1 = get_position_data(location_data_path)
    except FileNotFoundError as e:
        print("The file you requested wasn't found! ", e)

    # try:
    #     xar2, yar2 = get_position_data("data/position_data2.txt")
    # except FileNotFoundError as e:
    #     print("The file you requested wasn't found! ", e)

    ax1.clear()
    ax1.scatter(xar1, yar1, color="b", label="User 1", marker="*", s=30)
    try:
        ax1.scatter(xar1[0], yar1[0], color="y", label="User 1 Start Position", marker=">", s=70)
    except:
        pass

    # Add title and axis names
    plt.title("Users' Location and Trajectories")
    plt.xlabel('x-position')
    plt.ylabel('y-position')
    ax1.legend()
    # plt.legend()


plt.title("Users' Location and Trajectories")
plt.xlabel('x-position')
plt.ylabel('y-position')
ani = animation.FuncAnimation(fig, animate, interval=1000)

# Show graphic
plt.show()

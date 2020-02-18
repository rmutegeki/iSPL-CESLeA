import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

# img = plt.imread("image.png")
# fig, ax1 = plt.subplots()
# ax1.imshow(img, extent=[0, 200, 0, 200])

# fig = plt.figure()
# ax1 = fig.add_subplot(1, 1, 1)
fig, ax1 = plt.subplots()
point1 = [2.3, 0.09]
point2 = [7.6, 9.14]
point3 = [-4.6, 12.6]
point4 = [-10.8, -2.282]
x_plot1 = [point1[0], point2[0], point3[0], point4[0]]
y_plot1 = [point1[1], point2[1], point3[1], point4[1]]
wall_11 = [-1.87, 10.3]
wall_12 = [2.5, 8.6]
wall_13 = [-2, -2.9]
wall_14 = [-5.7, -0.13]

wall_2 = np.array([[-12, -2], [-8, 15], [10, 10], [6,-2]])

wall_513 = np.array([[-3, 12], [-11, -26], [24.776, -32.35], [30.68, 7.9], [-3, 12]])
tab1 = np.array([[-0.699, -12.8325], [1.44, -2.636]])
tab2 = np.array([[3.35, -16.47], [6.34, -2.01]])
tab3 = np.array([[9.73, -16.38], [12.18, -3.68]])
tab4 = np.array([[13.8, -18.66], [16.1, -2.74]])

def drawTextbox(x, y, txt="text", size=22, rotation=65):
    plt.text(x, y, txt, size=size, rotation=rotation,
             ha="center", va="center",
             bbox=dict(boxstyle="round",
                       ec=(1., 0.5, 0.5),
                       fc=(1., 0.8, 0.8),
                       )
             )
def get_position_data(file):
    user_data = open(file, "r").read()
    data_array = user_data.split("\n")
    xar = []
    yar = []
    for line in data_array:
        if len(line) > 1 :
            x, y = line.split(",")
            xar.append(float(x))
            yar.append(float(y))
    return xar, yar


def animate(i):

    xar1, yar1 = [], []
    xar2, yar2 = [], []
    try:
        xar1, yar1 = get_position_data("data/position_data1.txt")
    except FileNotFoundError as e:
        print("The file you requested wasn't found! ", e)

    ax1.clear()
    # plt.plot(x_plot1, y_plot1)
    # plt.plot(x_wall1, y_wall1, fillstyle='full')
    # plt.plot(wall_2[:,0], wall_2[:,1],linewidth=15, color='k')
    plt.plot(wall_513[:,0], wall_513[:,1], linewidth=15)
    # plt.plot(tab1[:, 0], tab1[:, 1], linewidth=35, color='b')
    # plt.plot(tab2[:, 0], tab2[:, 1], linewidth=35, color='b')
    # plt.plot(tab3[:, 0], tab3[:, 1], linewidth=35, color='b')
    drawTextbox(1.44, -7.21, "  table  ", size=12, rotation=65)
    drawTextbox(5.9, -8.15, "  table  ", size=12, rotation=65)
    drawTextbox(11.2, -8.67, "  table  ", size=12, rotation=65)
    drawTextbox(15.6, -9.5, "  table  ", size=12, rotation=65)
    drawTextbox(20, -11.5, "  table  ", size=12, rotation=65)

    drawTextbox(-1.94, -22.9, "table", size=12, rotation=65)
    drawTextbox(2.78, -23.76, "table", size=12, rotation=65)
    drawTextbox(7.94, -24.69, "table", size=12, rotation=65)
    drawTextbox(12.4, -25.42, "table", size=12, rotation=65)
    drawTextbox(16.94, -26.15, "table", size=12, rotation=65)

    drawTextbox(4.34, 6.52, "table", size=12, rotation=65)
    drawTextbox(8.57, 5.79, "table", size=12, rotation=65)
    drawTextbox(13.96, 5.27, "table", size=12, rotation=65)
    drawTextbox(18.38, 4.54, "table", size=12, rotation=65)
    drawTextbox(23.06, 3.81, "table", size=12, rotation=65)

    try:
        # ax1.scatter(xar1[-5:], yar1[-5:], color="b", label="User", marker="*", s=30)
        ax1.scatter(xar1, yar1, color="b", label="User", marker="*", s=30)
        ax1.scatter(xar1[0], yar1[0], color="y", label="User Start Position", marker=">", s=70)
    except:
        pass

    # Add title and axis names
    plt.title("User's Location and Trajectory")
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

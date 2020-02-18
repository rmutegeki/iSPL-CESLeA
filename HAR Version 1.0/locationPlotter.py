import matplotlib.animation as animation
import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)


def animate(i):
    pull_data = open("position.txt", "r").read()
    data_array = pull_data.split("\n")
    xar1 = []
    yar1 = []
    xar2 = []
    yar2 = []
    for line in data_array:
        if len(line) > 1:
            x1, y1, x2, y2 = line.split(",")
            xar1.append(float(x1))
            yar1.append(float(y1))
            xar2.append(float(x2))
            yar2.append(float(y2))
    ax1.clear()
    ax1.scatter(xar1, yar1, color="b", label="UserPosition", marker="*", s=20)
    ax1.scatter(xar2, yar2, color="b", label="UserPosition", marker=">", s=20)


ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()

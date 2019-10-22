import matplotlib.animation as animation
import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)


def animate(i):
    pull_data = open("position.txt", "r").read()
    data_array = pull_data.split("\n")
    xar = []
    yar = []
    for line in data_array:
        if len(line) > 1:
            x, y = line.split(",")
            xar.append(float(x))
            yar.append(float(y))
    ax1.clear()
    ax1.scatter(xar, yar, color="m", label="UserPosition", marker="n", s=20)


ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()

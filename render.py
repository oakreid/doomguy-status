# use python 3.6+

from math import ceil
from matplotlib import image, offsetbox, pyplot
from psutil import sensors_battery
from random import randrange

def loadImage(path):
    return offsetbox.OffsetImage(image.imread(path), zoom=1)

# load in required graphics
stbar = image.imread("graphics/stbar.png")
facelist = []
for healthrange in range(5):
    faces = []
    for orientation in range(3):
        faces.append(loadImage(f"graphics/stfst{healthrange}{orientation}.png"))
    facelist.append(faces)
rednumbers = [loadImage(f"graphics/winum{n}.png") for n in range(10)]
redpercent = loadImage("graphics/wipcnt.png")

# get relevant system info
battery_percent = int(sensors_battery()[0])

# formatting
pyplot.rcParams["figure.dpi"] = 141
fig, ax = pyplot.subplots()
fig.subplots_adjust(bottom=0, top=1, left=0, right=1)
fig.canvas.toolbar.pack_forget()
fig.canvas.set_window_title("Status Bar")

# run program loop
while True:
    # reset plot
    pyplot.cla()
    ax.imshow(stbar)
    ax.axis("off")
    fig.set_size_inches(4.5, .45)

    # rebuild image list
    images = [
        (facelist[5 - ceil(battery_percent / 20)][randrange(3)], 160, 16), # face
    ]
    if battery_percent == 100: # battery percent "health"
        images += [
            (rednumbers[1], 60, 0),
            (rednumbers[0], 70, 0),
            (rednumbers[0], 80, 0),
        ]

    # add images to plot
    ax.scatter(
        [x for image, x, y in images],
        [y for image, x, y in images],
        facecolors='none',
        edgecolors='none',
    )
    for image, x, y in images:
        ab = offsetbox.AnnotationBbox(image, (x, y), frameon=False)
        ax.add_artist(ab)
    
    # display for a second
    pyplot.pause(1)

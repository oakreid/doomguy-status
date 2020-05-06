# use python 3.6+

from math import ceil, floor
from matplotlib import image, offsetbox, pyplot
from psutil import sensors_battery
from random import randrange

ZOOM = 1
DPI = 141
PIXEL_WIDTH = 320
PIXEL_HEIGHT = 32
CENTER_X = PIXEL_WIDTH / 2
CENTER_Y = PIXEL_HEIGHT / 2
INCHES_WIDTH = float(PIXEL_WIDTH) / DPI * 2
INCHES_HEIGHT = float(PIXEL_HEIGHT) / DPI * 2
REDNUM_Y = CENTER_Y - 5
ONES_BATTERY_X = CENTER_X - 82
TENS_BATTERY_X = CENTER_X - 94

def loadImage(path):
    return offsetbox.OffsetImage(image.imread(path), zoom=ZOOM)

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
pyplot.rcParams["figure.dpi"] = DPI
fig, ax = pyplot.subplots()
fig.subplots_adjust(bottom=0, top=1, left=0, right=1)   # get rid of plot padding
fig.canvas.toolbar.pack_forget()                        # hide matplotlib toolbar
fig.canvas.set_window_title("Status Bar")

# run program loop
while True:
    # reset plot
    pyplot.cla()
    ax.imshow(stbar)
    ax.axis("off")
    fig.set_size_inches(INCHES_WIDTH, INCHES_HEIGHT)
   
    # rebuild image list
    images = [
        (facelist[5 - ceil(battery_percent / 20)][randrange(3)], CENTER_X, CENTER_Y),  # face
        (redpercent, CENTER_X - 69, REDNUM_Y),  # percentage sign, always in the same place
    ]
    if battery_percent == 100: # battery percent "health"
        images += [
            (rednumbers[1], CENTER_X - 104, REDNUM_Y),
            (rednumbers[0], TENS_BATTERY_X, REDNUM_Y),
            (rednumbers[0], ONES_BATTERY_X, REDNUM_Y),
        ]
    elif battery_percent > 9:
        images += [
            (rednumbers[floor(battery_percent / 10)], TENS_BATTERY_X, REDNUM_Y),
            (rednumbers[battery_percent % 10], ONES_BATTERY_X, REDNUM_Y),
        ]
    else:
        images.append((rednumbers[battery_percent], ONES_BATTERY_X, REDNUM_Y))

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

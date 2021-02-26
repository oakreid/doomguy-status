from math import ceil, floor
from os import environ
from random import randrange
from re import search

from matplotlib import image, offsetbox, pyplot
from psutil import cpu_percent, net_if_stats, sensors_battery


# constants
ZOOM = 1
DPI = 141
PIXEL_WIDTH = 320
PIXEL_HEIGHT = 32
CENTER_X = PIXEL_WIDTH / 2
CENTER_Y = PIXEL_HEIGHT / 2
INCHES_WIDTH = float(PIXEL_WIDTH) / DPI * 2
INCHES_HEIGHT = float(PIXEL_HEIGHT) / DPI * 2
REDNUM_Y = CENTER_Y - 5
ARMSTAB_X = CENTER_X - 37
ARMSNUMS_ROW1_Y = CENTER_Y - 9
ARMSNUMS_ROW2_Y = CENTER_Y + 1
ARMSNUMS_COL1_X = CENTER_X - 47
ARMSNUMS_COL2_X = CENTER_X - 35
ARMSNUMS_COL3_X = CENTER_X - 23
ONES_BATTERY_X = CENTER_X - 82
TENS_BATTERY_X = CENTER_X - 94
HUNDRED_BATTERY_X = CENTER_X - 104
PERCENT_BATTERY_X = CENTER_X - 69
ONES_CPU_X = CENTER_X + 48
TENS_CPU_X = CENTER_X + 36
HUNDRED_CPU_X = CENTER_X + 26
PERCENT_CPU_X = CENTER_X + 61
HUNDREDS_TIMELEFT_X = CENTER_X - 150
TENS_TIMELEFT_X = CENTER_X - 138
ONES_TIMELEFT_X = CENTER_X - 126
KEY_X = CENTER_X + 82
BLUE_KEY_Y = CENTER_Y - 10
YELLOW_KEY_Y = CENTER_Y
RED_KEY_Y = CENTER_Y + 10
try:
    DOOM_DIR = environ["DOOM_DIR"]
except KeyError:
    DOOM_DIR = "."

# helper functions
def get_armsnum(num: int):
    return armsnums_yellow[num]

try:
    from plumbum.cmd import iw
    def get_mcs(device: str):
        try:
            return int(search(r"rx.*MCS (\d+) .*", iw[device]["link"]())[1])
        except:
            return -1
except ImportError:
    def get_mcs(device: str):
        return 666

def load_image(path: str):
    return offsetbox.OffsetImage(image.imread(f"{DOOM_DIR}/graphics/{path}"), zoom=ZOOM)


# load in required graphics
stbar = image.imread(f"{DOOM_DIR}/graphics/stbar.png")
facelist = [[load_image(f"stfst{healthrange}{orientation}.png") for orientation in range(3)] for healthrange in range(5)]
faceouch = load_image("stfouch1.png")
rednumbers = [load_image(f"winum{n}.png") for n in range(10)]
redpercent = load_image("wipcnt.png")
redminus = load_image("sttminus.png")
armstab = load_image("starms.png")
armsnums_yellow = {n: load_image(f"stysnum{n}.png") for n in range(1, 7)}
armsnums_grey = {n: load_image(f"stgnum{n}.png") for n in range(1, 7)}
keyimgs = [load_image(f"stkeys{n}.png") for n in range(6)]

# formatting
pyplot.rcParams["figure.dpi"] = DPI
fig, ax = pyplot.subplots()
fig.subplots_adjust(bottom=0, top=1, left=0, right=1)   # get rid of plot padding
fig.canvas.toolbar.pack_forget()                        # hide matplotlib toolbar
fig.canvas.set_window_title("Status Bar")


# main program loop
def main():
    while True:

        # reset plot
        pyplot.cla()
        ax.imshow(stbar)
        ax.axis("off")
        fig.set_size_inches(INCHES_WIDTH, INCHES_HEIGHT)
     
        # get relevant system info
        battery_data = sensors_battery()
        cpu_usage_percent = int(cpu_percent())
        net_if_info = net_if_stats()
        eth_if_stats = next((stats for interface, stats in net_if_info.items() if interface.startswith("e") and stats.isup), None)
        wireless_if_name = next((interface for interface, stats in net_if_info.items() if interface.startswith("w") and stats.isup), None)


        # rebuild image list
        images = [
            (redpercent, PERCENT_BATTERY_X, REDNUM_Y),  # health percentage sign
            (redpercent, PERCENT_CPU_X, REDNUM_Y),      # cpu usage percentage sign
            (armstab, ARMSTAB_X, CENTER_Y),
            (get_armsnum(1), ARMSNUMS_COL1_X, ARMSNUMS_ROW1_Y),
            (get_armsnum(2), ARMSNUMS_COL2_X, ARMSNUMS_ROW1_Y),
            (get_armsnum(3), ARMSNUMS_COL3_X, ARMSNUMS_ROW1_Y),
            (get_armsnum(4), ARMSNUMS_COL1_X, ARMSNUMS_ROW2_Y),
            (get_armsnum(5), ARMSNUMS_COL2_X, ARMSNUMS_ROW2_Y),
            (get_armsnum(6), ARMSNUMS_COL3_X, ARMSNUMS_ROW2_Y),
        ]  # these are always in the same place

        if battery_data:
            battery_percent = int(battery_data.percent)
            battery_minsleft = min(int(battery_data.secsleft / 60), 999)
            images.append((facelist[5 - ceil(battery_percent / 20)][randrange(3)], CENTER_X, CENTER_Y))  # face

            # battery percent remaining "health"
            if battery_percent == 100:
                images += [
                    (rednumbers[1], HUNDRED_BATTERY_X, REDNUM_Y),
                    (rednumbers[0], TENS_BATTERY_X, REDNUM_Y),
                    (rednumbers[0], ONES_BATTERY_X, REDNUM_Y),
                ]
            elif battery_percent >= 10:
                images += [
                    (rednumbers[floor(battery_percent / 10)], TENS_BATTERY_X, REDNUM_Y),
                    (rednumbers[battery_percent % 10], ONES_BATTERY_X, REDNUM_Y),
                ]
            else:
                images.append((rednumbers[battery_percent], ONES_BATTERY_X, REDNUM_Y))

            # time (minutes) left on battery charge "ammo"
            if battery_minsleft >= 100:
                images += [
                    (rednumbers[floor(battery_minsleft / 100)], HUNDREDS_TIMELEFT_X, REDNUM_Y),
                    (rednumbers[floor(battery_minsleft % 100 / 10)], TENS_TIMELEFT_X, REDNUM_Y),
                    (rednumbers[battery_minsleft % 10], ONES_TIMELEFT_X, REDNUM_Y),
                ]
            elif battery_minsleft >= 10:
                images += [
                    (rednumbers[floor(battery_minsleft / 10)], TENS_TIMELEFT_X, REDNUM_Y),
                    (rednumbers[battery_minsleft % 10], ONES_TIMELEFT_X, REDNUM_Y),
                ]
            elif battery_minsleft <= 0:  # usually indicates the device is charging
                images += [
                    (redminus, HUNDREDS_TIMELEFT_X, REDNUM_Y),
                    (redminus, TENS_TIMELEFT_X, REDNUM_Y),
                    (redminus, ONES_TIMELEFT_X, REDNUM_Y),
                ]
            else:
                images.append((rednumbers[battery_minsleft], ONES_TIMELEFT_X, REDNUM_Y))
        else:  # usually indicates the device was just plugged into or unplugged from a power source
            images += [
                (faceouch, CENTER_X, CENTER_Y),
                (redminus, TENS_BATTERY_X, REDNUM_Y),
                (redminus, ONES_BATTERY_X, REDNUM_Y),
                (redminus, HUNDREDS_TIMELEFT_X, REDNUM_Y),
                (redminus, TENS_TIMELEFT_X, REDNUM_Y),
                (redminus, ONES_TIMELEFT_X, REDNUM_Y),
            ]
       
        # cpu usage percent "armor"
        if cpu_usage_percent == 100:
             images += [
                (rednumbers[1], HUNDRED_CPU_X, REDNUM_Y),
                (rednumbers[0], TENS_CPU_X, REDNUM_Y),
                (rednumbers[0], ONES_CPU_X, REDNUM_Y),
            ]
        elif cpu_usage_percent >= 10:
            images += [
                (rednumbers[floor(cpu_usage_percent / 10)], TENS_CPU_X, REDNUM_Y),
                (rednumbers[cpu_usage_percent % 10], ONES_CPU_X, REDNUM_Y),
            ]
        else:
            images.append((rednumbers[cpu_usage_percent], ONES_CPU_X, REDNUM_Y))

        # network connection status "keys"
        if eth_if_stats:  # ethernet interface exists and is up
            if eth_if_stats.speed >= 1000:
                images.append((keyimgs[0], KEY_X, BLUE_KEY_Y))
            if eth_if_stats.speed >= 100:
                images.append((keyimgs[1], KEY_X, YELLOW_KEY_Y))
            if eth_if_stats.speed >= 10:
                images.append((keyimgs[2], KEY_X, RED_KEY_Y))
        elif wireless_if_name:  # wireless interface exists and is up
            rx_mcs = get_mcs(wireless_if_name)
            if rx_mcs >= 8:
                images.append((keyimgs[3], KEY_X, BLUE_KEY_Y))
            if rx_mcs >= 3:
                images.append((keyimgs[4], KEY_X, YELLOW_KEY_Y))
            if rx_mcs >= 0:
                images.append((keyimgs[5], KEY_X, RED_KEY_Y))

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

        # refresh once per second
        pyplot.pause(1)


if __name__ == "__main__":
    main()

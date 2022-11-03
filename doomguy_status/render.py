import re
from calendar import monthrange
from datetime import datetime
from math import ceil, floor
from pkg_resources import resource_filename
from random import randrange

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
ONES_HEALTH_X = CENTER_X - 82
TENS_HEALTH_X = CENTER_X - 94
HUNDREDS_HEALTH_X = CENTER_X - 104
PERCENT_HEALTH_X = CENTER_X - 69
ONES_ARMOR_X = CENTER_X + 48
TENS_ARMOR_X = CENTER_X + 36
HUNDREDS_ARMOR_X = CENTER_X + 26
PERCENT_ARMOR_X = CENTER_X + 61
HUNDREDS_AMMO_X = CENTER_X - 150
TENS_AMMO_X = CENTER_X - 138
ONES_AMMO_X = CENTER_X - 126
KEY_X = CENTER_X + 82
BLUE_KEY_Y = CENTER_Y - 10
YELLOW_KEY_Y = CENTER_Y
RED_KEY_Y = CENTER_Y + 10
BULL_Y = CENTER_Y - 9
SHEL_Y = CENTER_Y - 3
RCKT_Y = CENTER_Y + 3
CELL_Y = CENTER_Y + 9
BSRC_TENS_X = CENTER_X + 121
BSRC_ONES_X = CENTER_X + 125
BSRC_TENTHS_X = CENTER_X + 143
BSRC_HUNDREDTHS_X = CENTER_X + 147


# helper functions
try:
    from i3ipc import Connection
    i3 = Connection()
    def get_focused_workspace():
        return i3.get_tree().find_focused().workspace().num
except ImportError:
    def get_focused_workspace():
        return 1

try:
    from plumbum.cmd import iw
    def get_mcs(device: str):
        try:
            return int(re.search(r"rx.*MCS (\d+) .*", iw[device]["link"]())[1])
        except:
            return -1
except ImportError:
    def get_mcs(device: str):
        return 666

try:
    from plumbum.cmd import pactl
    def get_volume_value():
        try:
            volume_data = pactl["list"]["sinks"]()
            return int([match[1] for match in re.finditer(r"\n\s*Volume\:.*/\s*(\d+)%", volume_data)][-1])
        except:
            return None
except ImportError:
    def get_volume_value():
        return None

def get_armsnum(num: int, focused_workspace: int):
    return smallnums_yellow[num] if num == focused_workspace else smallnums_grey[num]


def load_image(path: str):
    return offsetbox.OffsetImage(image.imread(resource_filename("doomguy_status", f"graphics/{path}")), zoom=ZOOM)


# load in required graphics
stbar = image.imread(resource_filename("doomguy_status", "graphics/stbar.png"))
facelist = [[load_image(f"stfst{healthrange}{orientation}.png") for orientation in range(3)] for healthrange in range(5)]
faceouch = load_image("stfouch1.png")
facegod = load_image("stfgod0.png")
rednumbers = [load_image(f"winum{n}.png") for n in range(10)]
redpercent = load_image("wipcnt.png")
redminus = load_image("sttminus.png")
armstab = load_image("starms.png")
smallnums_yellow = [load_image(f"stysnum{n}.png") for n in range(10)]
smallnums_grey = [load_image(f"stgnum{n}.png") for n in range(7)]
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
        volume_value = get_volume_value()
        cpu_usage_percent = int(cpu_percent())
        net_if_info = net_if_stats()
        eth_if_stats = next((stats for interface, stats in net_if_info.items() if interface.startswith("e") and stats.isup), None)
        wireless_if_name = next((interface for interface, stats in net_if_info.items() if interface.startswith("w") and stats.isup), None)
        focused_workspace = get_focused_workspace()
        time_now = datetime.now()

        # rebuild image list
        images = [
            (redpercent, PERCENT_HEALTH_X, REDNUM_Y),   # health percentage sign
            (redpercent, PERCENT_ARMOR_X, REDNUM_Y),    # cpu usage percentage sign
            (armstab, ARMSTAB_X, CENTER_Y),
            (get_armsnum(1, focused_workspace), ARMSNUMS_COL1_X, ARMSNUMS_ROW1_Y),
            (get_armsnum(2, focused_workspace), ARMSNUMS_COL2_X, ARMSNUMS_ROW1_Y),
            (get_armsnum(3, focused_workspace), ARMSNUMS_COL3_X, ARMSNUMS_ROW1_Y),
            (get_armsnum(4, focused_workspace), ARMSNUMS_COL1_X, ARMSNUMS_ROW2_Y),
            (get_armsnum(5, focused_workspace), ARMSNUMS_COL2_X, ARMSNUMS_ROW2_Y),
            (get_armsnum(6, focused_workspace), ARMSNUMS_COL3_X, ARMSNUMS_ROW2_Y),
        ]  # these are always in the same place

        if battery_data:
            battery_percent = int(battery_data.percent)
            if battery_percent == 100 and cpu_usage_percent == 100:
                images.append((facegod, CENTER_X, CENTER_Y))  # godmode
            else:
                images.append((facelist[5 - ceil(battery_percent / 20)][randrange(3)], CENTER_X, CENTER_Y))  # face

            # battery percent remaining "HEALTH"
            if battery_percent == 100:
                images.append((rednumbers[1], HUNDREDS_HEALTH_X, REDNUM_Y))
            if battery_percent >= 10:
                images.append((rednumbers[floor(battery_percent / 10) % 10], TENS_HEALTH_X, REDNUM_Y))
            images.append((rednumbers[battery_percent % 10], ONES_HEALTH_X, REDNUM_Y))
        else:  # usually indicates the device was just plugged into or unplugged from a power source
            images += [
                (faceouch, CENTER_X, CENTER_Y),
                (redminus, TENS_HEALTH_X, REDNUM_Y),
                (redminus, ONES_HEALTH_X, REDNUM_Y),
            ]

        if volume_value is not None:
            volume_value = min(volume_value, 999)

            # volume value "AMMO"
            if volume_value >= 100:
                images.append((rednumbers[floor(volume_value / 100)], HUNDREDS_AMMO_X, REDNUM_Y))
            if volume_value >= 10:
                images.append((rednumbers[floor(volume_value / 10) % 10], TENS_AMMO_X, REDNUM_Y))
            images.append((rednumbers[volume_value % 10], ONES_AMMO_X, REDNUM_Y))
        else:  # indicates volume is muted or cannot get volume info
            images += [
                (redminus, HUNDREDS_AMMO_X, REDNUM_Y),
                (redminus, TENS_AMMO_X, REDNUM_Y),
                (redminus, ONES_AMMO_X, REDNUM_Y),
            ]

        # cpu usage percent "ARMOR"
        if cpu_usage_percent == 100:
            images.append((rednumbers[1], HUNDREDS_ARMOR_X, REDNUM_Y))
        if cpu_usage_percent >= 10:
            images.append((rednumbers[floor(cpu_usage_percent / 10) % 10], TENS_ARMOR_X, REDNUM_Y))
        images.append((rednumbers[cpu_usage_percent % 10], ONES_ARMOR_X, REDNUM_Y))

        # network connection status "KEYS"
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

        # month / 12 "BULL"
        images += [
            (smallnums_yellow[floor(time_now.month / 10)], BSRC_TENS_X, BULL_Y),
            (smallnums_yellow[time_now.month % 10], BSRC_ONES_X, BULL_Y),
            (smallnums_yellow[1], BSRC_TENTHS_X, BULL_Y),
            (smallnums_yellow[2], BSRC_HUNDREDTHS_X, BULL_Y),
        ]

        # day / days in month "SHEL"
        days_in_month = monthrange(time_now.year, time_now.month)[1]
        images += [
            (smallnums_yellow[floor(time_now.day / 10)], BSRC_TENS_X, SHEL_Y),
            (smallnums_yellow[time_now.day % 10], BSRC_ONES_X, SHEL_Y),
            (smallnums_yellow[floor(days_in_month / 10)], BSRC_TENTHS_X, SHEL_Y),
            (smallnums_yellow[days_in_month % 10], BSRC_HUNDREDTHS_X, SHEL_Y),
        ]

        # hour / 24 "RCKT"
        images += [
            (smallnums_yellow[floor(time_now.hour / 10)], BSRC_TENS_X, RCKT_Y),
            (smallnums_yellow[time_now.hour % 10], BSRC_ONES_X, RCKT_Y),
            (smallnums_yellow[2], BSRC_TENTHS_X, RCKT_Y),
            (smallnums_yellow[4], BSRC_HUNDREDTHS_X, RCKT_Y),
        ]

        # minute / 60 "CELL"
        images += [
            (smallnums_yellow[floor(time_now.minute / 10)], BSRC_TENS_X, CELL_Y),
            (smallnums_yellow[time_now.minute % 10], BSRC_ONES_X, CELL_Y),
            (smallnums_yellow[6], BSRC_TENTHS_X, CELL_Y),
            (smallnums_yellow[0], BSRC_HUNDREDTHS_X, CELL_Y),
        ]

        # add images to plot
        img_x_y = list(zip(*images))
        ax.scatter(img_x_y[1], img_x_y[2], facecolors='none', edgecolors='none')
        for image, x, y in images:
            ax.add_artist(offsetbox.AnnotationBbox(image, (x, y), frameon=False))

        # refresh once per second
        pyplot.pause(1)


if __name__ == "__main__":
    main()

from i3ipc import Connection, Event

i3 = Connection()

def float_status(i3, e):
    status_bar = i3.get_tree().find_titled("Status Bar")
    if status_bar:
        status_bar[0].command("floating enable")
        status_bar[0].command("move position 640 1016")
        status_bar[0].command("sticky enable")
        status_bar[0].command("border pixel 0")

i3.on(Event.WINDOW_FOCUS, float_status)
i3.on(Event.WORKSPACE_MOVE, float_status)

if __name__ == "__main__":
    i3.main()

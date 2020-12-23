from i3ipc import Connection

i3 = Connection()

def float_status(i3, e):
    status_bar = i3.get_tree().find_titled("Status Bar")
    if status_bar:
        status_bar[0].command("floating enable")
        status_bar[0].command("move position 636 1020")
        status_bar[0].command("sticky enable")
        status_bar[0].command("border pixel 0")

i3.on('window::new', float_status)

i3.main()

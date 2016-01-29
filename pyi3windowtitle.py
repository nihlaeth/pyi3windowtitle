#!/usr/bin/python
"""Keep track of window title of the window currently in focus."""
import sys
import i3ipc
import unicodedata
from daemon import daemon
from tools.colorlog import log, LOGLEVEL

LOGLEVEL.set_level("verbose")

# pylint: disable=invalid-name

stdin = "/dev/null"
stdout = "/dev/null"
stderr = "/dev/null"
pidfile = "/home/nihlaeth/pyi3windowtitle/pyi3windowtitle.pid"


def on_window_focus(i3, _):
    """Callback for window focus event."""
    focused = i3.get_tree().find_focused()
    window_class = focused.window_class
    window_name = focused.name
    info_string = "class= %s title= %s" % (window_class, window_name)
    info_string = unicodedata.normalize(
        'NFKD',
        info_string).encode('ascii', 'ignore')
    with open("/home/nihlaeth/.i3/windowfocus", "w") as focus_file:
        focus_file.write(info_string)


def serve():
    """Set up window change event."""
    i3 = i3ipc.Connection()
    i3.on("window::focus", on_window_focus)
    # write current window info to file
    on_window_focus(i3, None)
    i3.main()


class MyDaemon(daemon.Daemon):
    """Daemonize RemoteControl."""

    def run(self):
        """Start the actual process."""
        log("info", "running!")
        serve()

if __name__ == "__main__":
    daemon = MyDaemon(
        pidfile,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr)
    if len(sys.argv) == 2:
        if sys.argv[1] == 'start':
            log("info", "Starting...")
            daemon.start()
            log("info", "Started!")
        elif sys.argv[1] == 'stop':
            daemon.stop()
        elif sys.argv[1] == 'restart':
            daemon.restart()
        else:
            log("fail", "Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        log("info", "usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)

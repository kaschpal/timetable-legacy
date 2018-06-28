#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from MainWindow import MainWindow

from TimeTable import TimeTable

timeTab = TimeTable()


class UPlan(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        win = MainWindow(self)
        win.show_all()


if __name__ == "__main__":
    #app = UPlan()
    #exit_status = app.run(sys.argv)
    #sys.exit(exit_status)

    # create window
    win = MainWindow()
    win.connect("destroy", win.quit)
    win.show_all()

    # load config from the statefile
    #win.loadFile( ttfileName )

    # mainloop
    Gtk.main()




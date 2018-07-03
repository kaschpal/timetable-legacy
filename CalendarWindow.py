import gi

import language

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import datetime
import config

class Calendar(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.connect("map", self.showHandler)

        self.__calendar = Gtk.Calendar()
        self.pack_start( self.__calendar, False, True, 0)

        self.__textview = Gtk.TextView()
        self.pack_start( self.__textview, True, True, 0)


    def showHandler(self, wid):
        self.update()

    def update(self):
        from uplan import timeTab
        global timeTab

        self.show_all()
        print("calendar show")



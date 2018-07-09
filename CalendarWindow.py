import gi
import language
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import datetime
import config
import calendar

class Calendar(Gtk.Box):
    def __init__(self, parent):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.connect("map", self.__showHandler)
        self.parent = parent

        self.textview = MemoView(parent=self)
        self.calendar = MemoCalendar(parent=self)
        self.pack_start(self.calendar, False, True, 0)

        self.pack_start(self.textview, True, True, 0)

    def __showHandler(self, wid):
        self.update()

    def update(self):
        self.show_all()
        self.calendar.update()
        self.textview.update()

class MemoCalendar(Gtk.Calendar):
    def __init__(self, parent):
        Gtk.Calendar.__init__(self)
        self.parent = parent
        self.connect("day-selected", self.__selectHandler)
        self.connect("day-selected-double-click", self.__doubleclickHandler)
        self.connect("month-changed", self.update)

        # call selection handler on current (initial) selection
        self.__selectHandler(self)

    # return date of selected day as pythondatetime-object
    def __getSelectedDate(self):
        d = self.props.day
        m = self.props.month+1
        y = self.props.year
        return datetime.date(day=d,month=m,year=y)

    def __selectHandler(self, wid):
        # look, if there is already a text in the buffer, which has to be saved
        # before switching
        txt = self.parent.textview.getText()
        if txt != "":
            self.parent.textview.save()
        # needed by the textview
        self.currentSelectionDate = self.__getSelectedDate()
        # set textwid to selected entry
        self.parent.textview.loadEntry(self.currentSelectionDate)
        # if saved, update marks
        if txt != "":
            self.update()

    # set timetable to doubleclicked week/day and switch to it
    def __doubleclickHandler(self, wid):
        # set selected date in timetable
        date = self.__getSelectedDate()
        self.parent.parent.weekWid.setDate(date)
        # switch to timetable
        self.parent.parent.stack.set_visible_child_name("timetable")


    def update(self, wid=None):
        print("cal update")

        m = self.props.month + 1
        y = self.props.year

        # determine how many days the current month has
        last = calendar.monthrange(y, m)[1]

        self.clear_marks() # remove all previous
        # mark days with entry
        for d in range(1, last+1):
            if self.parent.parent.environment.timeTab.getCalendarEntry(datetime.date(day=d,month=m,year=y)) != "":
                self.mark_day(d)


class MemoView(Gtk.TextView):
    def __init__(self, parent):
        Gtk.TextView.__init__(self)

        self.buffer = Gtk.TextBuffer()
        self.set_buffer(self.buffer)
        self.parent = parent
        # when disappearing, save content
        self.connect("unmap", self.save)

    # load the entry of the date into the buffer
    def loadEntry(self, date):
        s = self.parent.parent.environment.timeTab.getCalendarEntry(date)
        self.buffer.set_text(s)

    def update(self):
        # get marked entry from calendar and set text
        date = self.parent.calendar.currentSelectionDate
        self.loadEntry(date)

    def save(self, wid=None):
        txt = self.getText()
        date = self.parent.calendar.currentSelectionDate
        self.parent.parent.environment.timeTab.putCalendarEntry(date, txt)

    # get text from buffer as string
    def getText(self):
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        return self.buffer.get_text(start, end, False)












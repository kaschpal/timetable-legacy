import gi
import language

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio
import datetime
import config


class DayGrid(Gtk.Grid):
    def __init__(self, date, parent):
        Gtk.Grid.__init__(self)
        self.date = date
        self.weekday = date.isoweekday()
        self.__updateList = []
        self.parent = parent
        # gtk.grid does not store this, it is used to remove/add the last line
        self.__number_of_rows = 1   # starts at one, the first has no entries

        # some space between the columns of the grid
        self.set_column_spacing(5)

        # show date and weekday
        dateLab = DateLabel( self )

        # behind the label of the day comes a checkbutton, if the day
        # is off school
        offBox = Gtk.Box(spacing=1)
        offBox.pack_start(dateLab, True, True, 0)

        self.offToggle = Gtk.CheckButton()
        self.__offDayHandler = self.offToggle.connect("toggled", self.__offButtonToggled)
        offBox.pack_start(self.offToggle, True, True, 0)

        # calendar-button
        button = CalendarButton(parent=self)
        offBox.pack_start(button, False, True, 0)
        self.__updateList.append(button)

        self.attach(offBox, 3, 0, 1, 1)
        self.__updateList.append(dateLab)

        # the period-matrix
        for period in range(1,self.parent.window.environment.setting_number_of_periods_show()+1):
            self.__add_line(period)

        # update to see if the day is off school
        self.update()
    
    # add one line to the daygrid
    def __add_line(self, period):
        # three labels
        periodLab = Gtk.Label()
        classEnt = ClassEntry(weekday=self.weekday , period=period, parent=self)
        topicEnt = TopicEntry(weekday=self.weekday , period=period, parent=self)

        # add widgets, which have to be updated automatically
        self.__updateList.append(classEnt)
        self.__updateList.append(topicEnt)

        topicEnt.set_width_chars(config.topicLen)

        periodLab.set_text(str(period))
        classEnt.set_width_chars(6)

        # emits a signal when the Enter key is pressed, connected to the
        # callback function cb_activate
        classEnt.connect("activate", self.__classActivate)
        topicEnt.connect("activate", self.__topicActivate)

        # in the grid:
        self.attach(periodLab, 1, period+1, 1, 1)
        self.attach(classEnt, 2, period+1, 1, 1)
        self.attach(topicEnt, 3, period+1, 1, 1)

        # activate all items. this is necessary, if the lines are added via the settings menu
        periodLab.show()
        classEnt.show()
        topicEnt.show()
        
        # keep track
        self.__number_of_rows = self.__number_of_rows + 1


    # remove the last line
    def remove_last_line(self):
        self.remove_row(self.__number_of_rows)
        # keep track
        self.__number_of_rows = self.__number_of_rows - 1
        # remove the class- and topic entries from the updatelist
        # otherwise they are not garbage collected AND always updated
        del self.__updateList[-2:]
    
    # add one more line
    def add_last_line(self):
        self.__add_line(self.__number_of_rows)

    # set lines to desired value
    def set_to_line(self, number):
        number = number + 1 # the fist row is only counted in the daygrid, not is sense of the method
        if number > self.__number_of_rows: # add lines
            lines_to_add = number - self.__number_of_rows
            for _ in range(0, lines_to_add):
                self.add_last_line()

        elif number < self.__number_of_rows: # remove lines
            lines_to_del = self.__number_of_rows - number
            for _ in range(0, lines_to_del):
                self.remove_last_line()
        else:                               # no change
            pass


    def __offButtonToggled(self, wid):
        if self.offToggle.get_active() == False:
            self.parent.window.environment.timeTab.addDayOff(self.date)
        else:
            self.parent.window.environment.timeTab.removeDayOff(self.date)

        self.parent.update()


    def __classActivate(self, entry):
        # retrieve the content of the widget
        name = entry.get_text()
        period = entry.period
        #weekday = entry.weekday


        # inject the class in the period-table
        self.parent.window.environment.timeTab.injectClassName(date=self.date, period=period, name=name)
        entry.update()

        # update the weekgrid, lessons may have shifted
        self.parent.update()

    def __topicActivate(self, entry):
        # retrieve the content of the widget
        topic = entry.get_text()
        period = entry.period
        date = self.date

        # inject the class in the period-table
        self.parent.window.environment.timeTab.changeTopic(date, period, topic)
        entry.update()

    def update(self):
        # at first, update all widgets
        for wid in self.__updateList:
            wid.update()

        # update the checkbox
        # block because only marking by hand should call the handler
        with self.offToggle.handler_block(self.__offDayHandler):
            if self.parent.window.environment.timeTab.dayOff(self.date):
                self.offToggle.set_active(False)
                for wid in self.__updateList:
                    if type(wid) is not CalendarButton: # dont deactivate the memos
                        wid.set_sensitive(False)
            else:
                self.offToggle.set_active(True)
                for wid in self.__updateList:
                    wid.set_sensitive(True)

        self.offToggle.handler_unblock(self.__offDayHandler)

        for wid in self.__updateList:
            wid.update()

        # mark everything grey in addition, if it is a free day

class CalendarButton(Gtk.Button):
    def __init__(self, parent):
        Gtk.Button.__init__(self)
        self.parent = parent

        # init icons
        icon = Gio.ThemedIcon(name="starred-symbolic")
        self.__empty_image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        icon = Gio.ThemedIcon(name="software-update-urgent-symbolic")
        self.__not_empty_image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.__current_image = None

        # calendar textview
        self.__calBuffer = Gtk.TextBuffer()
        self.__calView = Gtk.TextView(buffer=self.__calBuffer)

        # calendar bubble
        self.__popover = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(self.__calView, True, True, 10)
        self.__popover.add(vbox)
        self.__popover.connect("map", self.__loadBuf)
        self.__popover.connect("closed", self.__saveBuf)


        self.connect("clicked", self.__togglePopup)
        self.connect("map", self.__loadBuf )
        self.__updateIcon()

    def update(self):
        self.__loadBuf(self.__popover)

    def __updateIcon(self):
        # set icon
        if self.__getText() == "":
            self.__setEmpty()
        else:
            self.__setNotEmpty()
        self.__current_image.show()

    # on close of popup, save entry and update
    def __saveBuf(self, popover):
        self.parent.parent.window.environment.timeTab.putCalendarEntry(self.parent.date, self.__getText())
        self.__updateIcon()

    # on open of popup, get entry and update
    def __loadBuf(self, popover):
        memo = self.parent.parent.window.environment.timeTab.getCalendarEntry(self.parent.date)
        self.__calBuffer.set_text(memo)
        self.__updateIcon()


    # get text from buffer as string
    def __getText(self):
        start = self.__calBuffer.get_start_iter()
        end = self.__calBuffer.get_end_iter()
        return self.__calBuffer.get_text(start, end, False)

    # activate popup
    def __togglePopup(self, button):
        self.__popover.set_relative_to(button)
        self.__popover.show_all()
        self.__popover.popup()

    # set icon to empty entry
    def __setEmpty(self):
        if self.__current_image is not None:
            self.remove(self.__current_image)
        self.add(self.__empty_image)
        self.__current_image = self.__empty_image

    # set icon to filled entry
    def __setNotEmpty(self):
        if self.__current_image is not None:
            self.remove(self.__current_image)
        self.add(self.__not_empty_image)
        self.__current_image = self.__not_empty_image


class ClassEntry(Gtk.Entry):
    def __init__(self, weekday, period, parent):
        Gtk.Entry.__init__(self)
        self.parent = parent

        self.weekday = weekday
        self.period = period

        self.update()

    def update(self):
        self.date = self.parent.date

        # if it is a day off, the display no text at all
        if self.parent.parent.window.environment.timeTab.dayOff(self.date) == True:
            self.set_text( "" )
            return

        # set to the last entry
        className = self.parent.parent.window.environment.timeTab.getClassName(self.date, self.period)

        # if it is a dot-entry, display the dot
        if  self.parent.parent.window.environment.timeTab.classNameIsDotEntry(self.date, self.period):
            className = "." + className

        self.set_text( className )

        # if the class has been set on this day, paint red
        # also, if it is a dot-entry
        if self.parent.parent.window.environment.timeTab.classNameIsEdited(self.date, self.period)\
                or self.parent.parent.window.environment.timeTab.classNameIsDotEntry(self.date, self.period):
            RED = Gdk.Color(50000, 0, 0)
            self.modify_fg(Gtk.StateFlags.NORMAL, RED)
        else:
            self.modify_fg(Gtk.StateFlags.NORMAL, None)





class TopicEntry(Gtk.Entry):
    def __init__(self, weekday, period, parent):
        Gtk.Entry.__init__(self)
        self.parent = parent

        self.weekday = weekday
        self.period = period

        self.update()


    def update(self):
        self.date = self.parent.date

        # if it is a day off, the display no text at all
        if self.parent.parent.window.environment.timeTab.dayOff(self.date) == True:
            self.set_text( "" )
            return

        self.set_text( self.parent.parent.window.environment.timeTab.getTopic(self.date, self.period) )

# the date is read from the parent, to do an update
# via the update method
class DateLabel(Gtk.Label):
    def __init__(self, parent):
        Gtk.Label.__init__(self)
        self.parent = parent
        self.update()

    def update(self):
        self.date = self.parent.date
        weekday = self.date.isoweekday()
        dayName = language.weekdays[weekday]

        # if today, write this behind the date
        if self.date == datetime.date.today():
            todayTag = "(" + language.todayName + ")"
        else:
            todayTag = ""

        # text to be displayed over the day
        self.set_text('{}, {}.{}. {}'.format(dayName, self.date.day, self.date.month, todayTag) )

        # and write todays date bold
        if self.date == datetime.date.today():
            self.set_markup("<b>" + self.get_text() +"</b>")




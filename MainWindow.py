import gi
import language
import datetime
import config
from WeekGrid import WeekGrid
from SequenceWindow import ClassNotebook
from CalendarWindow import  Calendar
from TimeTable import TimeTable
from gi.repository import Gtk, Gio
gi.require_version('Gtk', '3.0')


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self):
        Gtk.Window.__init__(self)
        #Gtk.Window.__init__(self, title="UPlan", application=app)
        self.resizeable = False

        # load the statfile and with it the active timetable
        self.environment = Environment(self)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        self.add(vbox)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)
        
        # the timetable
        self.weekWid = WeekGrid( datetime.date.today(), window=self )
        self.stack.add_titled(self.weekWid, "timetable", language.timeTableName)

        # the sequences
        self.classNoteb = ClassNotebook(parent=self)
        self.stack.add_titled(self.classNoteb, "sequence", language.sequenceName)
        
        # the calendar 
        self.calendar = Calendar(parent=self)
        self.stack.add_titled(self.calendar, "calendar", language.calendarName)

        ## the switcher
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(self.stack)
        stack_switcher.props.halign = Gtk.Align.CENTER
        #vbox.set_center_widget(stack_switcher)
        vbox.pack_start(stack_switcher, True, True, 0)
        vbox.pack_end(self.stack, False, False, 0)

        self.__header()


        # dont resize
        self.set_resizable(False)

        # update on change of view
        self.stack.connect("notify::visible-child", self.__stackSwitched )


    def __stackSwitched(self, wid, gparamstring):
        if self.classNoteb.currentPage is not None:
            self.classNoteb.currentPage.save()

        self.weekWid.update()
        print("weekupd")


    def __header(self):
        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.set_titlebar(self.hb)
        # after loading filename
        self.props.title = language.applicationName + ": " + str(self.environment.currentFileName)


        # popover for menu
        popover = Gtk.PopoverMenu()

        # create actions
        load_action = Gio.SimpleAction.new("load", None)
        self.add_action(load_action)
        load_action.connect("activate", self.__loadClicked)

        save_action = Gio.SimpleAction.new("save", None)
        self.add_action(save_action)
        save_action.connect("activate", self.__saveClicked)

        new_action = Gio.SimpleAction.new("new", None)
        self.add_action(new_action)
        new_action.connect("activate", self.__newClicked)

        quit_save_action = Gio.SimpleAction.new("quit_save", None)
        self.add_action(quit_save_action)
        quit_save_action.connect("activate", self.__quit_save)

        quit_without_saving_action = Gio.SimpleAction.new("quit_without_saving", None)
        self.add_action(quit_without_saving_action)
        quit_without_saving_action.connect("activate", self.__quit_without_saving)

        # populate menu
        menu = Gio.Menu()
        menu.insert_item( 0, Gio.MenuItem.new( language.openTimetable, "win.load" ) )
        menu.insert_item( 1, Gio.MenuItem.new( language.saveTimetable, "win.save" ) )
        menu.insert_item( 2, Gio.MenuItem.new( language.newTimetable, "win.new" ) )
        menu.insert_item( 3, Gio.MenuItem.new( language.quit_with_saving, "win.quit_save" ) )
        menu.insert_item( 4, Gio.MenuItem.new( language.quit_without_saving, "win.quit_without_saving" ) )

        #menu button
        button = Gtk.MenuButton.new()
        popover = Gtk.Popover.new_from_model(button, menu)
        button.set_popover(popover)
        icon = Gio.ThemedIcon(name="open-menu-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        self.hb.pack_end(button)

        # settings button
        button = SettingsButton(window=self)
        self.hb.pack_end(button)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")

        # left previous week
        button = Gtk.Button()
        button.add(Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE))
        box.add(button)
        button.connect("clicked", self.__prevWeekclicked)

        # right: next week
        button = Gtk.Button()
        button.add(Gtk.Arrow(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE))
        box.add(button)
        button.connect("clicked", self.__nextWeekclicked)

        # current week
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-open-recent-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        box.add(button)
        button.connect("clicked", self.__currentWeekclicked)

        #
        #
        # test button: only enable, if in debug-mode
        if self.environment.setting_debug() == True:
            button = Gtk.Button()
            icon = Gio.ThemedIcon(name="view-refresh")
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
            button.add(image)
            box.add(button)
            button.connect("clicked", self.__testclicked)
            self.test = False 
        #
        #
        #

        self.hb.pack_start(box)

    #
    #
    #
    def __testclicked(self, button):
        for wid in self.weekWid.widList:
            wid.add_last_line()
    #
    #
    #

    def __nextWeekclicked(self, button):
        nxdate = self.weekWid.date + datetime.timedelta(weeks=1)
        self.weekWid.setDate(nxdate)

    def __prevWeekclicked(self, button):
        nxdate = self.weekWid.date - datetime.timedelta(weeks=1)
        self.weekWid.setDate(nxdate)

    def __currentWeekclicked(self, button):
        nxdate =  datetime.date.today()
        self.weekWid.setDate(nxdate)

    def __saveClicked(self, button, action):
        # not yet saved, no filename selected
        if self.environment.currentFileName == None:
            filename = self.__chooseFilename()
            if filename == None:
                return
        self.environment.saveCurrentFile( )

    def __chooseFilename(self):
        # choose new filename and directory
        dialog = Gtk.FileChooserDialog(language.chooseFileName, self,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_current_name(language.default_filename_for_saving)

        # add filters for pickle-files an all files
        filter_p = Gtk.FileFilter()
        filter_p.set_name(language.timetableName)
        filter_p.add_mime_type("text/x-python")
        filter_p.add_pattern("*.p")
        dialog.add_filter(filter_p)

        filter_all = Gtk.FileFilter()
        filter_all.set_name(language.allfilesName)
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            filename = None
        else:
            filename = None

        dialog.destroy()
        return filename


    def __newClicked(self, button, action):
        filename = self.__chooseFilename()

        if filename is None:
            return

        # delete everything
        self.environment.clear()

        # save under new filename
        self.environment.currentFileName = filename
        self.environment.saveCurrentFile()
        self.environment.saveState()
        self.environment.loadFile( self.environment.currentFileName )


    def __loadClicked(self, button, action):
        # create open dialog
        dialog = Gtk.FileChooserDialog(language.chooseFileName, self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        # add filters for pickle-files an all files
        filter_p = Gtk.FileFilter()
        filter_p.set_name(language.timetableName)
        filter_p.add_mime_type("text/x-python")
        filter_p.add_pattern("*.p")
        dialog.add_filter(filter_p)

        filter_all = Gtk.FileFilter()
        filter_all.set_name(language.allfilesName)
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self.environment.loadFile(filename)
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

    def quit(self, wid):
        if self.environment.setting_save_on_quit() == True:
            self.__quit_save(self, None)
        else:
            self.__quit_without_saving(self, None)

    def __quit_without_saving(self, wid, action):
        print("quit without saving")
        self.environment.saveState()
        Gtk.main_quit()

    def __quit_save(self, wid, action):
        print("quit save")
        # no filename choosen yet
        if self.environment.currentFileName == None:
            filename = self.__chooseFilename()
            if filename == None:
                return
            else:
                self.environment.currentFileName = filename

        self.environment.saveCurrentFile()
        self.environment.saveState()
        Gtk.main_quit()

# settings menu
#
#
class SettingsButton(Gtk.Button):
    def __init__(self, window):
        Gtk.Button.__init__(self)
        self.window = window

        # set icon
        icon = Gio.ThemedIcon(name="preferences-system-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.add(image)

        self.__popover = Gtk.Popover()
        grid = Gtk.Grid()
        grid.props.column_spacing = 5
        
        # spinbutton for number of periods per day
        lab = Gtk.Label(language.number_of_periods_show)
        lab.props.halign = Gtk.Align.START
        grid.attach(lab, 0, 0, 1, 1)
        spin = Gtk.SpinButton()
        # get min / max value
        minval, maxval = self.window.environment.settings.get_range("number-of-periods-show")[1]
        # adjustment
        adjustment = Gtk.Adjustment(0, minval, maxval, 1, 1, 0)
        spin.set_adjustment(adjustment)
        self.window.environment.settings.bind("number-of-periods-show", spin, "value", Gio.SettingsBindFlags.DEFAULT)
        grid.attach(spin, 1, 0, 1, 1)
        # immediately show/hide
        spin.connect("value-changed", self.__show_hide_lines)

        # switch for "show saturday"
        lab = Gtk.Label(language.show_saturday)
        lab.props.halign = Gtk.Align.START
        grid.attach(lab, 0, 1, 1, 1)
        sw = Gtk.Switch()
        self.window.environment.settings.bind("show-saturday", sw, "active", Gio.SettingsBindFlags.DEFAULT)
        grid.attach(sw, 1, 1, 1, 1)
        # immediately show/hide
        sw.connect("state-set", self.__show_hide_sat)

        # switch for "autosave on quit"
        lab = Gtk.Label(language.save_on_quit)
        lab.props.halign = Gtk.Align.START
        grid.attach(lab, 0, 2, 1, 1)
        sw = Gtk.Switch()
        self.window.environment.settings.bind("save-on-quit", sw, "active", Gio.SettingsBindFlags.DEFAULT)
        grid.attach(sw, 1, 2, 1, 1)

        # switch for "debug mode"
        lab = Gtk.Label(language.debug_mode)
        lab.props.halign = Gtk.Align.START
        grid.attach(lab, 0, 3, 1, 1)
        sw = Gtk.Switch()
        self.window.environment.settings.bind("debug", sw, "active", Gio.SettingsBindFlags.DEFAULT)
        grid.attach(sw, 1, 3, 1, 1)

        # signals
        self.__popover.add(grid)
        self.__popover.connect("map", self.__open)
        self.__popover.connect("closed", self.__close)
        self.connect("clicked", self.__togglePopup)

    # show / hide saturday
    def __show_hide_sat(self, sw, state):
        if state == True:
            self.window.weekWid.sat.show()
        else:
            self.window.weekWid.sat.hide()
    
    # show / hide lines
    def __show_hide_lines(self, spin):
        value = int(spin.props.value)
        for day in self.window.weekWid.widList:
            day.set_to_line(value)


    def update(self):
        pass

    # on close of popup
    def __close(self, popover):
        pass

    # on open of popup
    def __open(self, popover):
        pass

    # activate popup
    def __togglePopup(self, button):
        self.__popover.set_relative_to(button)
        self.__popover.show_all()
        self.__popover.popup()


class Environment():
    def __init__(self, parent):
        # load settings from local gesettings-file
        schema_source = Gio.SettingsSchemaSource.new_from_directory(config.programDirectory,
                                                                    Gio.SettingsSchemaSource.get_default(), False)
        schema = Gio.SettingsSchemaSource.lookup(schema_source, 'de.gymlan.timetable', False)
        if not schema:
            raise Exception("Cannot get GSettings  schema")
        self.settings = Gio.Settings.new_full(schema, None, config.programDirectory)

        self.parent = parent
        self.timeTab = TimeTable(environment=self)
        self.loadState()

    def saveFile(self, filename):
        self.timeTab.saveToFile( filename )

    def saveCurrentFile(self):
        self.saveFile(self.currentFileName)

    def loadFile(self, filename):
        # load the timetable from the statefile

        if filename == None or self.timeTab.loadFromFile( filename ) == False:
            try:
                self.parent.hb.props.title
            except AttributeError:
                pass
            else:
                self.parent.hb.props.title = (language.applicationName + ": " + "(neu)")
            self.currentFileName = None
            return

        # update, if widgets are already created (maybe this is the first call)
        try:
            self.parent.weekWid.update()
        except AttributeError:
            pass
        else:
            self.parent.weekWid.update()

        try:
            self.parent.hb.props.title
        except AttributeError:
            pass
        else:
            self.parent.hb.props.title = (language.applicationName + ": " + filename)

        # set new filename in statefile
        self.currentFileName = filename

    def saveState(self):
        self.settings.set_string("current-filename", self.currentFileName)

    def loadState(self):
        self.currentFileName = self.setting_current_filename()
        if self.currentFileName == "":
            self.currentFileName = None
        self.loadFile(self.currentFileName)

    def clear(self):
        #self.__saveEmptyState()
        self.loadState()
        self.timeTab.clear(self)
        self.parent.weekWid.update()

    # methods for retrieving settings
    def setting_number_of_periods_show(self):
        return self.settings.get_int('number-of-periods-show')
    def setting_number_of_periods_create(self):
        return self.settings.get_int('number-of-periods-create')
    def setting_show_saturday(self):
        return self.settings.get_boolean('show-saturday')
    def setting_debug(self):
        return self.settings.get_boolean('debug')
    def setting_save_on_quit(self):
        return self.settings.get_boolean('save-on-quit')
    def setting_current_filename(self):
        return self.settings.get_string('current-filename')






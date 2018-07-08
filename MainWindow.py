import gi
import language
import datetime
import config
from WeekGrid import WeekGrid
from SequenceWindow import ClassNotebook
from CalendarWindow import  Calendar
from gi.repository import Gtk, Gio
gi.require_version('Gtk', '3.0')


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self):
        Gtk.Window.__init__(self, title=language.applicationName)
        #Gtk.Window.__init__(self, title="UPlan", application=app)

        self.resizeable = False

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        self.add(vbox)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)
        
        # the timetable
        self.weekWid = WeekGrid( datetime.date.today() )
        self.stack.add_titled(self.weekWid, "timetable", language.timeTableName)

        # the sequences
        self.classNoteb = ClassNotebook()
        self.stack.add_titled(self.classNoteb, "sequence", language.sequenceName)
        
        # the calendar 
        self.calendar = Calendar(parent=self)
        self.stack.add_titled(self.calendar, "calendar", language.calendarName)

        ## the switcher
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(self.stack)
        #vbox.set_center_widget(stack_switcher)
        vbox.pack_start(stack_switcher, True, True, 0)
        vbox.pack_end(self.stack, False, False, 0)

        self.__header()

        # dont resize
        self.set_resizable(False)

        # update on change of view
        self.stack.connect("notify::visible-child", self.__stackSwitched )

        # load the statfile and with it the active timetable
        self.environment = Environment(self)

    def __stackSwitched(self, wid, gparamstring):
        if self.classNoteb.currentPage is not None:
            self.classNoteb.currentPage.save()

        self.weekWid.update()
        print("weekupd")


    def __header(self):
        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.hb.props.title = language.applicationName
        self.set_titlebar(self.hb)


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
        if config.debug() == True:
            button = Gtk.Button()
            icon = Gio.ThemedIcon(name="view-refresh")
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
            button.add(image)
            box.add(button)
            button.connect("clicked", self.__testclicked)
        #
        #
        #

        self.hb.pack_start(box)

    #
    #
    #
    def __testclicked(self, button):
        global timeTab
        print( config.programDirectory )
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
        if config.save_on_quit == True:
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


class Environment():
    def __init__(self, parent):
        self.parent = parent
        self.loadState()

    def saveFile(self, filename):
        from uplan import timeTab
        global timeTab
        timeTab.saveToFile( filename )

    def saveCurrentFile(self):
        self.saveFile(self.currentFileName)

    def loadFile(self, filename):
        # load the timetable from the statefile
        from uplan import timeTab
        global timeTab

        if filename == None or timeTab.loadFromFile( filename ) == False:
            self.parent.hb.props.title = (language.applicationName + ": " + "(neu)")
            self.currentFileName = None
            return

        self.parent.weekWid.update()
        self.parent.hb.props.title = (language.applicationName + ": " + filename)

        # set new filename in statefile
        self.currentFileName = filename

    def saveState(self):
        import pickle
        import config
        names = ["currentFileName"]
        l = [self.currentFileName]

        d = dict( zip( names, l ) )
        pickle.dump(d, open(config.stateFile, "wb"))

    def loadState(self):
        import pickle
        import config

        try:
            d = pickle.load(open(config.stateFile, "rb"))
        # no statefile yet created
        except FileNotFoundError:
            self.__saveEmptyState()
            self.loadState()
            return

        self.currentFileName = d["currentFileName"]
        self.loadFile(self.currentFileName)

    def __saveEmptyState(self):
        import pickle
        import config
        # first, create a dictionary with all tables
        names = ["currentFileName"]
        l = [ None ]

        d = dict( zip( names, l ) )
        pickle.dump(d, open(config.stateFile, "wb"))

    def clear(self):
        self.__saveEmptyState()
        self.loadState()
        from uplan import timeTab
        global timeTab
        timeTab.clear()
        self.parent.weekWid.update()






import gi

import language

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import datetime
import config


class ClassNotebook(Gtk.Notebook):
    def __init__(self):
        Gtk.Notebook.__init__(self)

        # here come all current tabs
        self.__tabs = []

        self.connect("map", self.showHandler)
        self.set_scrollable( True )

        self.__savelist = []

        self.currentPage = None


    def showHandler(self, wid):
        self.update()

    def update(self):
        from uplan import timeTab
        global timeTab

        # first, remove all
        for tab in self.__tabs:
            self.detach_tab(tab)


        # now add from the time table
        for name in timeTab.getClassList():
            #page = Gtk.Box()
            #page.add(SequenceWindow())
            page = SequenceTV(name, parent=self)
            self.append_page(page, Gtk.Label( name ))
            self.__tabs.append(page)

            page.update()

        self.show_all()




class SequenceTV(Gtk.ScrolledWindow):
    def __init__(self, name, parent):
        Gtk.ScrolledWindow.__init__(self )
        self.parent = parent

        self.name = name

        # a scrollbar for the child widget (that is going to be the textview)
        #scrolled_window = Gtk.ScrolledWindow()

        self.set_border_width(5)
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.nrBuf = Gtk.TextBuffer()
        self.dateBuf = Gtk.TextBuffer()
        self.periodBuf = Gtk.TextBuffer()
        self.sequenceBuf = Gtk.TextBuffer()

        nrLab = Gtk.Label()
        dateLab = Gtk.Label()
        periodLab = Gtk.Label()
        sequenceLab = Gtk.Label()

        vsep1 = Gtk.VSeparator()
        vsep2 = Gtk.VSeparator()
        vsep3 = Gtk.VSeparator()

        nrLab.set_text(language.numberName)
        dateLab.set_text(language.dateName)
        periodLab.set_text(language.periodName)
        sequenceLab.set_text(language.topicName)
        nrLab.set_width_chars(3)
        periodLab.set_width_chars(3)
        dateLab.set_width_chars(15)


        # a textview (displays the buffer)
        nrTextView = Gtk.TextView(buffer=self.nrBuf)
        dateTextView = Gtk.TextView(buffer=self.dateBuf)
        periodTextView = Gtk.TextView(buffer=self.periodBuf )
        sequenceTextView = Gtk.TextView(buffer=self.sequenceBuf)

        # wrap the text, if needed, breaking lines in between words
        nrTextView.set_wrap_mode(Gtk.WrapMode.WORD)
        dateTextView.set_wrap_mode(Gtk.WrapMode.WORD)
        periodTextView.set_wrap_mode(Gtk.WrapMode.WORD)
        sequenceTextView.set_wrap_mode(Gtk.WrapMode.WORD)


        #set justifications
        nrTextView.set_justification(Gtk.Justification.CENTER)
        dateTextView.set_justification(Gtk.Justification.RIGHT)
        periodTextView.set_justification(Gtk.Justification.CENTER)

        #set date/period are not to edit
        nrTextView.set_editable(False)
        dateTextView.set_editable(False)
        periodTextView.set_editable(False)

        # the topic should fill the rest of the empty space
        # and the textview should be expanded in the beginning
        sequenceLab.set_hexpand(True)
        sequenceTextView.set_vexpand(True)

        # x, then y
        grid = Gtk.Grid()
        grid.attach(nrLab, 0, 0, 1, 1)
        grid.attach(vsep1,  1, 0, 1, 2)
        grid.attach(dateLab, 2, 0, 1, 1)
        grid.attach(vsep2,  3, 0, 1, 2)
        grid.attach(periodLab, 4, 0, 1, 1)
        grid.attach(vsep3,  5, 0, 1, 2)
        grid.attach(sequenceLab, 6, 0, 1, 1)

        grid.attach(nrTextView, 0, 1, 1, 1)
        grid.attach(dateTextView, 2, 1, 1, 1)
        grid.attach(periodTextView, 4, 1, 1, 1)
        grid.attach(sequenceTextView, 6, 1, 1, 1)
        self.add(grid)

        # when the widget is visible, load the sequence and save it, when it becomes
        # invisible
        self.connect("map", self.__loadSequence  )
        self.connect("unmap", self.__saveSequence  )

        self.sequenceList = []


    # get the sequence when we become visible
    def __loadSequence(self, wid):
        from uplan import timeTab
        global timeTab

        self.sequenceList = timeTab.getSequence(self.name)
        self.parent.currentPage = self

        self.update()



    # put the sequence on change of the displayed class
    def __saveSequence(self, wid):
        from uplan import timeTab
        global timeTab

        start = self.sequenceBuf.get_start_iter()
        end = self.sequenceBuf.get_end_iter()
        self.sequenceList = self.sequenceBuf.get_text(start, end, False).split("\n")
        timeTab.putSequence(self.name, self.sequenceList)

        print("save")

    def save(self):
        self.__saveSequence(self)


    def update(self):
        from uplan import timeTab
        global timeTab

        name = self.name

        # set the date-column
        dates = [d for d, p in timeTab.getDatesOfClass(name)]
        dates = [language.weekdaysShort[d.isoweekday()] + "  " + "{0:02d}".format(d.day) + "." + "{0:02d}".format(d.month) + "." + str(d.year) for d in dates]
        datestxt = "\n".join(dates)
        self.dateBuf.set_text(datestxt)

        # set the period-column
        periods = [p for d, p in timeTab.getDatesOfClass(name)]
        periods = [str(p) for p in periods]
        txt = "\n".join(periods)
        self.periodBuf.set_text(txt)

        # set the nr-column
        ns = range(1, len(timeTab.getDatesOfClass(name)) + 1)
        ns = [str(n) for n in ns]
        txt = "\n".join(ns)
        self.nrBuf.set_text(txt)

        # set the sequence
        sl = self.sequenceList
        sl = [str(t) for t in sl]
        txt = "\n".join(sl)
        self.sequenceBuf.set_text(txt)



# -*- coding: utf-8 -*-
import datetime
import os

# real configuration
numberOfPeriodsShow = 9
numberOfPeriodsCreate = 15
showSaturday = False
savefile = "/home/ulrich/Dokumente/Schule/uplan.p"
DEBUG = False
save_on_quit = True

# stuff, which will likely never change
epoch = datetime.date(year=1970, month=1, day=1)
topicLen = 30
MAXDATES = 400

# configuration code
programDirectory = os.path.dirname( os.path.abspath(__file__) ) + os.sep
stateFile = programDirectory + "state.p"

# -*- coding: utf-8 -*-
import datetime
import os
from gi.repository import Gio

# stuff, which will likely never change
epoch = datetime.date(year=1970, month=1, day=1)
topicLen = 30
MAXDATES = 400

# configuration code
programDirectory = os.path.dirname( os.path.abspath(__file__) ) + os.sep
stateFile = programDirectory + "state.p"
dconfPath = "/apps/timetable/"


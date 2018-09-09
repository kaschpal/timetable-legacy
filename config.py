# -*- coding: utf-8 -*-
import datetime
import os
import locale
from gi.repository import Gio

# stuff, which will likely never change
epoch = datetime.date(year=1970, month=1, day=1)
topicLen = 30
MAXDATES = 400
maxdates_repeat = 100

# configuration code
programDirectory = os.path.dirname( os.path.abspath(__file__) ) + os.sep
stateFile = programDirectory + "state.p"
dconfPath = "/apps/timetable/"

# language
if os.name == "posix":      # UNIX
    language = locale.getdefaultlocale()[0].split("_")[0]
elif os.name == "nt":       # Windows
    import ctypes
    windll = ctypes.windll.kernel32
    language = locale.windows_locale[windll.GetUserDefaultUILanguage()].split("_")[0]
else:                       # at least try ...
    language = locale.getdefaultlocale()[0].split("_")[0]

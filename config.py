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

"""
# load gschema
schema_source = Gio.SettingsSchemaSource.new_from_directory(programDirectory, 
                Gio.SettingsSchemaSource.get_default(), False)
schema = Gio.SettingsSchemaSource.lookup(schema_source, 'de.gymlan.timetable', False)
if not schema:
    raise Exception("Cannot get GSettings  schema")
settings = Gio.Settings.new_full(schema, None, programDirectory)

# options and settings
def number_of_periods_show():
    return settings.get_int('number-of-periods-show')
def number_of_periods_create():
    return settings.get_int('number-of-periods-create')
def show_saturday():
    return settings.get_boolean('show-saturday')
def debug():
    return True
    return settings.get_boolean('debug')
def save_on_quit():
    return settings.get_boolean('save-on-quit')
"""

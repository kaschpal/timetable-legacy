import config

# german
if config.language == "de":
    applicationName = "Stundenplan"
    timeTableName = "Stundenplan"
    sequenceName = "Sequenz"
    calendarName = "Kalender"
    todayName = "heute"
    weekdays = {1: "Montag",
                2: "Dienstag",
                3: "Mittwoch",
                4: "Donnerstag",
                5: "Freitag",
                6: "Samstag",
                7: "Sonntag"}
    weekdaysShort = {1: "Mo",
                     2: "Di",
                     3: "Mi",
                     4: "Do",
                     5: "Fr",
                     6: "Sa",
                     7: "So"}
    numberName = "#"
    dateName = "Datum"
    periodName = "h"
    topicName = "Thema"
    chooseFileName = "Bitte Datei wählen"
    timetableName = "Stundenpläne"
    allfilesName = "Alle Dateien"
    openTimetable = "Stundenplan öffnen"
    saveTimetable = "Stundenplan speichern"
    newTimetable = "Neuer Stundenplan"
    quit_with_saving = "Beenden und speichern"
    quit_without_saving = "Beenden ohne speichern"
    default_filename_for_saving = "Unbenannt.p"
    number_of_periods_show = "Anzahl Stunden"
    show_saturday = "Samstag anzeigen"
    save_on_quit = "Beim Beenden speichern"
    debug_mode = "Debug-Modus"
    about = "Über " + applicationName
# english
else:
    applicationName = "Timetable"
    timeTableName = "timetable"
    sequenceName = "sequence"
    calendarName = "calendar"
    todayName = "today"
    weekdays = {1: "Monday",
                2: "Tuesday",
                3: "Wednesday",
                4: "Thursday",
                5: "Friday",
                6: "Saturday",
                7: "Sunday"}
    weekdaysShort = {1: "Mon",
                     2: "Tue",
                     3: "Wed",
                     4: "Thu",
                     5: "Fri",
                     6: "Sat",
                     7: "Sun"}
    numberName = "#"
    dateName = "date"
    periodName = "h"
    topicName = "topic"
    chooseFileName = "Please choose file"
    timetableName = "timetables"
    allfilesName = "all files"
    openTimetable = "open timetable"
    saveTimetable = "save timetable"
    newTimetable = "new timetable"
    quit_with_saving = "save and quit"
    quit_without_saving = "quit without saving"
    default_filename_for_saving = "new.p"
    number_of_periods_show = "periods to show"
    show_saturday = "show saturday"
    save_on_quit = "save when quitting"
    debug_mode = "debug mode"
    about = "About " + applicationName

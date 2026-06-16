from java.util import TimeZone
from java.lang import System

def printTimeZone():
    tz = TimeZone.getDefault()
    id = tz.getID()
    
    regiTzId = System.getProperty("rowcps.timezone")
    regiTz = TimeZone.getTimeZone(regiTzId)

    print "Default system timezone:{0}, Observes daylight: {1}".format(id, str(tz.useDaylightTime())) 
    print "Regi timezone:{0}, Observes daylight: {1}".format(regiTzId, str(regiTz.useDaylightTime())) 

def printAll():
    printTimeZone()
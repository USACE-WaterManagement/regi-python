# the java Calendar class is used to create java Date objects
from java.util import Calendar
from java.util import TimeZone
import sys
import getopt

def Usage():
    msg = """
    This file demonstrates how to utilize the Headless Stream Status functionality.
    This script is not meant to be executed by itself but should be executed from the RegiCLI.
    Among other things the RegiCLI opens the specified study and connects to the database using the specified
    credentials.  Once RegiCLI has completed the preliminary steps it will execute the specified python scripts
    and allow the scripts to call into the Java classes and methods.
    This file is an example of how the Stream Status functionality can be scripted.
    """
    print msg

def headless_examples():
    # This gets a scriptable Stream Status object.
    streamStatus = registry.getCalculation(1.0, "Status")

    # Time zone must be set because the Solaris time zone is UTC
    timeZone = TimeZone.getTimeZone("US/Central")
    # Configure the calendar
    startCal = Calendar.getInstance(timeZone)
    startCal.clear()
    startCal.set(Calendar.YEAR, 2016)
    startCal.set(Calendar.MONTH, 3)
    startCal.set(Calendar.DATE, 2)
    startCal.set(Calendar.HOUR_OF_DAY, 0)
    # Month 4 means May to java...

    # If the filepath does not end in .jpg then the image will be saved in png format.

    # Generate a single image,
    #   at a single location within a basin,
    #   at single date,
    #   with a single chart template
    #   and write to specified file.
    print "Demonstrating a call to generateStreamStatusImage"
    streamFilepath = "../headless/StatusGraphics/streamStatus.jpg"
    streamStatus.generateStreamStatusImage("SWF", "RSRT2", "Flood Control Focus View", startCal.getTime(), 800, 600, streamFilepath)

    #print "Demonstrating a call  to generateReservoirStatusImage"
    #reservoirFilePath = "../headless/StatusGraphics/reservoirStatus.jpg"
    #streamStatus.generateReservoirStatusImage("SWF", "GPVT2", "Flood Control Focus View", startCal.getTime(), 800, 600, reservoirFilePath)

    #print "Demonstrating a call to generateReleasesStatusImage"
    #releasesFilePath = "../headless/StatusGraphics/releasesStatus.jpg"
    #streamStatus.generateReleasesStatusImage("SWF", "WTYT2", "Flood Control Focus View", startCal.getTime(), 800, 600, releasesFilePath)
    
if __name__ == "__builtin__":
    Usage()
    headless_examples()

if __name__ == "__main__":
    Usage()
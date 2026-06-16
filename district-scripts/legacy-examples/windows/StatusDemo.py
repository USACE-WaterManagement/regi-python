# the java Calendar class is used to create java Date objects
from java.util import Calendar
from java.util import TimeZone
from usace.rowcps.headless import LoggingOptions


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
    # Description of: LoggingOptions.setDbMessageLevel(int level)
    #
    # Adds Time Series logging messages in the OracleTimeSeriesDaoImpl.  Recommended
    # level is 2, as this provides basic information about the time series
    # retrieval/storage.
    #
    # Message Level | Description
    # --------------|-------------------------------------------------------------------------------------------------------------------------------|
    # <=0           | Default value, does not do anything.  Lower values do not change behavior.                                                    |
    # 1             | Logs message when no data is found.  Logs message when data is found, how much was retrieved or stored, and how long it took. |
    # 2             | Adds message with name of time series, and the units to retrieve/store.                                                       |
    # 3             | Adds message with the current time.                                                                                           |
    # 4             | Adds message with first 10 dates and values from each time series.                                                            |
    # >4            | Same as 4, but shows all values retrieved from each time series.  Higher values do not change behavior.                       |
    # --------------|-------------------------------------------------------------------------------------------------------------------------------|
    
    LoggingOptions.setDbMessageLevel(2)
    
    # This gets a scriptable Stream Status object.
    streamStatus = registry.getCalculation(1.0, "Status")

    # Time zone must be set because the Solaris time zone is UTC
    timeZone = TimeZone.getTimeZone("US/Central")
    
    # Configure the calendar
    # Default start is top of the current hour
    startCal = Calendar.getInstance(timeZone)
    startCal.set(Calendar.MINUTE, 0)
    startCal.set(Calendar.SECOND, 0)
    startCal.set(Calendar.MILLISECOND, 0)
    
    # Calendar can be adjusted using the following functions:
    #   startCal.set(Calendar.DATE, 1)          # Sets the date of the calendar.
    #   startCal.set(Calendar.HOUR_OF_DAY, 1)   # Sets the hour of the day to 0100 (1-24)
    #   startCal.set(Calendar.YEAR, 2020)       # Sets the year
    #   startCal.set(Calendar.MONTH, 4)         # Sets the month (month 4 means May to Java)

    # If the filepath does not end in .jpg then the image will be saved in png format.

    # Generate a single image,
    #   at a single location within a basin,
    #   at single date,
    #   with a single chart template
    #   and write to specified file.
    #   Supports PNG and jpg output
    
    path = "headless\\StatusGraphics\\"
    
    print "Demonstrating a call to generateStreamStatusImage"
    streamStatus.generateStreamStatusImage("SWF", "RSRT2", "Flood Control Focus View", startCal.getTime(), 800, 600, path + "streamStatus.jpg")

    print "Demonstrating a call  to generateReservoirStatusImage"
    streamStatus.generateReservoirStatusImage("SWF", "GPVT2", "Flood Control Focus View", startCal.getTime(), 800, 600, path + "reservoirStatus.jpg")

    print "Demonstrating a call to generateReleasesStatusImage"
    streamStatus.generateReleasesStatusImage("SWF", "WTYT2", "Flood Control Focus View", startCal.getTime(), 800, 600, path + "releasesStatus.jpg")


if __name__ == "__builtin__":
    Usage()
    headless_examples()


if __name__ == "__main__":
    Usage()

# the java Calendar class is used to create java Date objects
from java.util import Calendar
from java.util import TimeZone
import os, sys
from usace.rowcps.headless import LoggingOptions

sys.path.insert(0, os.path.abspath(".."))


def Usage():
    msg = """
    This file demonstrates how to utilize the Headless Basin Pie functionality.
    This script is not meant to be executed by itself but should be executed from the RegiCLI.
    Among other things the RegiCLI opens the specified study and connects to the database using the specified
    credentials.  Once RegiCLI has completed the preliminary steps it will execute the specified python scripts
    and allow the scripts to call into the Java classes and methods.
    This file is an example of how the Basin Pie functionality can be scripted.
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
    
    # This gets a scriptable Basin Pie object.
    basinPie = registry.getCalculation(1.0, "Status")
    

    ######################################################################################
    #                                                                                    #
    # Please refer to the functions for the parametrization for generating the graphics. #
    #                                                                                    #
    ######################################################################################


    # Time zone must be set because the Solaris time zone is UTC
    timeZone = TimeZone.getTimeZone("US/Central")

    # Configure the calendar for the date and time of the Basin Pie graphic
    # Defaults to top of current hour
    startCal = Calendar.getInstance(timeZone)
    startCal.set(Calendar.MINUTE, 0)
    startCal.set(Calendar.SECOND, 0)
    startCal.set(Calendar.MILLISECOND, 0)
    
    # Calendar can be adjusted using the following functions:
    #   startCal.set(Calendar.DATE, 1)          # Sets the date of the calendar.
    #   startCal.set(Calendar.HOUR_OF_DAY, 1)   # Sets the hour of the day to 0100 (1-24)
    #   startCal.set(Calendar.YEAR, 2020)       # Sets the year
    #   startCal.set(Calendar.MONTH, 4)         # Sets the month (month 4 means May to Java)

    # When generating multiple image files the filepath may contain replacement keywords.
    # If these keywords are found in the filepath they are replaced with named piece of data.
    # Once the replacements are made, illegal characters in the filename are replaced with '_'.
    # The following keywords are currently recognized:
    #     %date%
    #     %office_id%
    #     %location_id%
    #     %chart_template_id%
    #     %basin_id%
    #     %image_format%
    # Example: filepath like:
    #       "headless\\%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png"
    # Will generate the following files:
    #       headless\\SWF_Trinity_R_Basin_RSRT2_Conservation Pool (static)_2016-04-02T00_00_00Z.png

    filepath = "\\headless\\%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png"

    # Generate a basin pie image,
    #   for each of the specified locations in the specified basin,
    #   for each of the dates,
    #   for each of the chart templates
    #   replace %% patterns in the specified filepath template
    #   and write each image to its generated filepath
    # print "Demonstrating a call to generateBasinPieImages"
    # generateBasinPieImages("SWF", ["LOLT2"], "Trinity_R_Basin",
    #                       dates, 700, 807,
    #                       ["Design Capacity"],
    #                       filepath)

    # Generate an image
    #   for the locations found in a basin
    #   for each of the dates,
    #   for each of the chart templates
    #   replace %% patterns in the specified filepath template
    #   and write each image to its generated filepath

    print "Demonstrating a call to generateBasinPieImageForGroup"    
    generateBasinPieImageForGroup("SWF", "DAWT2", "Trinity", startCal.getTime(), 700, 807,"Design Capacity","headless\\generateBasinPieImageForGroup\\test_%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png")
    
    print "Demonstrating a call to generateBasinPieImagesForGroup"
    generateBasinPieImagesForGroup("SWF", ["LVNT2","STIT2"], "XYZ", [startCal.getTime()], 700, 807,["Design Capacity"],"headless\\generateBasinPieImagesForGroup\\test_%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png")

    print "Demonstrating a call to generateBasinPieImageForBasin"
    generateBasinPieImageForBasin("SWF", "DAWT2", "Trinity_R_Basin", startCal.getTime(), 700, 807,"Design Capacity","headless\\generateBasinPieImageForBasin\\test_%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png")

    print "Demonstrating a call to generateBasinPieImagesForBasin"
    generateBasinPieImagesForBasin("SWF", ["LOLT2","DAWT2"], "Trinity_R_Basin", [startCal.getTime()], 700, 807,["Design Capacity"],"headless\\generateBasinPieImagesForBasin\\test_%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png")

    print "Demonstrating a call to generateAllBasinPieImagesForBasin"
    generateAllBasinPieImagesForBasin("SWF", "Trinity_R_Basin", [startCal.getTime()], 800, 600, ["Conservation Pool (static)"], "headless\\generateAllForBasin\\test_%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png")

    print "Demonstrating a call to generateAllBasinPieImagesForGroup"
    generateAllBasinPieImagesForGroup("SWF", "XYZ", [startCal.getTime()], 800, 600, ["Conservation Pool (static)"], "headless\\generateAllForGroup\\test_%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png")


def generateBasinPieImageForBasin(office_id, location_id, basin_id,
                          date, width, height,
                          chart_template_id,
                          filepath):
    """

    :param office_id: The office id used for finding the specified locations, basin and chart_template
    :param location_id: The location for which the basin pie image is desired
    :param basin_id: The id of the Basin
    :param date: This specifies the time for which the image should be generated
    :param width: width in pixels
    :param height: height in pixels
    :param chart_template_id: The id of the chart template to use.
    :param filepath: Path of where to write the file.
    """
    basinPie = registry.getCalculation(1.0, "Status")
    basinPie.generateBasinPieImageForBasin(office_id, location_id, basin_id,
                          date, width, height,
                          chart_template_id,
                          filepath)


def generateBasinPieImagesForBasin(office_id, location_ids, basin_id,
                          dates, width, height,
                          chart_template_ids,
                          filepath):
    # type: (string, string, string, [date], int, int, [string], string) -> void
    """

    :param office_id: The office id used for finding the specified locations, basin and chart_template
    :param location_ids: A list of the locations for which basin pie images are desired
    :param basin_id: The id of the Basin
    :param dates: A list of the times for which the image should be generated
    :param width: width in pixels
    :param height: height in pixels
    :param chart_template_ids: The ids of the chart template to use.
    :param filepath: Path (template) of where to write the file.
    """
    basinPie = registry.getCalculation(1.0, "Status")
    basinPie.generateBasinPieImagesForBasin(office_id, location_ids, basin_id,
                          dates, width, height,
                          chart_template_ids,
                          filepath)


def generateBasinPieImageForGroup(office_id, location_id, group_id,
                          date, width, height,
                          chart_template_id,
                          filepath):
    # type: (string, string, string, [date], int, int, [string], string) -> void
    """

    :param office_id: The office id used for finding the specified locations, basin and chart_template
    :param location_id: A list of the locations for which basin pie images are desired
    :param group_id: The id of the Group
    :param date: A list of the times for which the image should be generated
    :param width: width in pixels
    :param height: height in pixels
    :param chart_template_id: The ids of the chart template to use.
    :param filepath: Path (template) of where to write the file.
    """
    basinPie = registry.getCalculation(1.0, "Status")
    basinPie.generateBasinPieImageForGroup(office_id, location_id, group_id,
                          date, width, height,
                          chart_template_id,
                          filepath)


def generateBasinPieImagesForGroup(office_id, location_ids, group_id,
                          dates, width, height,
                          chart_template_ids,
                          filepath):
    # type: (string, string, string, [date], int, int, [string], string) -> void
    """

    :param office_id: The office id used for finding the specified locations, basin and chart_template
    :param location_ids: A list of the locations for which basin pie images are desired
    :param group_id: The id of the Group
    :param dates: A list of the times for which the image should be generated
    :param width: width in pixels
    :param height: height in pixels
    :param chart_template_ids: The ids of the chart template to use.
    :param filepath: Path (template) of where to write the file.
    """
    basinPie = registry.getCalculation(1.0, "Status")
    basinPie.generateBasinPieImagesForGroup(office_id, location_ids, group_id,
                          dates, width, height,
                          chart_template_ids,
                          filepath)


def generateAllBasinPieImagesForBasin(office_id, basin_id,
                          dates, width, height,
                          chart_template_ids,
                          filepath):
    basinPie = registry.getCalculation(1.0, "Status")
    basinPie.generateAllBasinPieImagesForBasin(office_id,  basin_id,
                          dates, width, height,
                          chart_template_ids,
                          filepath)


def generateAllBasinPieImagesForGroup(office_id, group_id,
                          dates, width, height,
                          chart_template_ids,
                          filepath):
    basinPie = registry.getCalculation(1.0, "Status")
    basinPie.generateAllBasinPieImagesForGroup(office_id,  group_id,
                          dates, width, height,
                          chart_template_ids,
                          filepath)


if __name__ == "__builtin__":
    Usage()
    headless_examples()


if __name__ == "__main__":
    Usage()

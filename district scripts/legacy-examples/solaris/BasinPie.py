# the java Calendar class is used to create java Date objects
from java.util import Calendar
from java.util import TimeZone
import os, sys
import getopt
sys.path.insert(0, os.path.abspath(".."))
#from examples import printInfo

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
    #printInfo.printAll()
    # This gets a scriptable Basin Pie object.
    basinPie = registry.getCalculation(1.0, "Status")
    

    ######################################################################################
    #                                                                                    #
    # Please refer to the functions for the parametrization for generating the graphics. #
    #                                                                                    #
    ######################################################################################

    # Configure the calendar for the date and time of the Basin Pie graphic
    timeZone = TimeZone.getTimeZone("US/Central")
    startCal = Calendar.getInstance(timeZone)
    startCal.clear()
    startCal.set(Calendar.YEAR, 2016)
    startCal.set(Calendar.MONTH, 4)
    startCal.set(Calendar.DATE, 5)
    startCal.set(Calendar.HOUR_OF_DAY, 0)
    # Month 4 means May to java...

    # If the filepath does not end in .jpg then the image will be saved in png format.
    filepath = "../headless/basin.jpg"
    #filepath = "../headless/basin.png"

    # Generate a single image,
    #   at a single location within a basin,
    #   at single date,
    #   with a single chart template
    #   and write to specified file.
    #print "Demonstrating a call to generateBasinPieImageForBasin"
    #generateBasinPieImageForBasin("SWF", "RRLT2", "Trinity_R_Basin",
    #                      startCal.getTime(), 700, 807,
    #                      "Design Capacity",
    #                      filepath)

    # Generate multiple images
    # First built the dates
    dates = []
    for i in range(0, 3):
        dates.append(startCal.getTime())
        startCal.add(Calendar.DATE, 1)

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
    #       "../headless/%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png"
    # Will generate the following files:
    #       ../headless/SWF_Trinity_R_Basin_RSRT2_Conservation Pool (static)_2016-04-02T00_00_00Z.png

    filepath = "../headless/%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png"

    # Generate a basin pie image,
    #   for each of the specified locations in the specified basin,
    #   for each of the dates,
    #   for each of the chart templates
    #   replace %% patterns in the specified filepath template
    #   and write each image to its generated filepath
#    print "Demonstrating a call to generateBasinPieImages"
#    generateBasinPieImages("SWF", ["LOLT2"], "Trinity_R_Basin",
#                          dates, 700, 807,
#                          ["Design Capacity"],
#                          filepath)

    # Generate an image
    #   for the locations found in a basin
    #   for each of the dates,
    #   for each of the chart templates
    #   replace %% patterns in the specified filepath template
    #   and write each image to its generated filepath

    print "Demonstrating a call to generateBasinPieImageForGroup"    
    generateBasinPieImageForGroup("SWF", "DAWT2", "Trinity", startCal.getTime(), 700, 807,"Design Capacity","../headless/generateBasinPieImageForGroup/test_%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png")
    
    print "Demonstrating a call to generateBasinPieImagesForGroup"
    generateBasinPieImagesForGroup("SWF", ["LVNT2","STIT2"], "XYZ", [startCal.getTime()], 700, 807,["Design Capacity"],"../headless/generateBasinPieImagesForGroup/test_%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png")

    print "Demonstrating a call to generateBasinPieImageForBasin"
    generateBasinPieImageForBasin("SWF", "DAWT2", "Trinity_R_Basin", startCal.getTime(), 700, 807,"Design Capacity","../headless/generateBasinPieImageForBasin/test_%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png")

    print "Demonstrating a call to generateBasinPieImagesForBasin"
    generateBasinPieImagesForBasin("SWF", ["LOLT2","DAWT2"], "Trinity_R_Basin", [startCal.getTime()], 700, 807,["Design Capacity"],"../headless/generateBasinPieImagesForBasin/test_%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png")

    print "Demonstrating a call to generateAllBasinPieImagesForBasin"
    generateAllBasinPieImagesForBasin("SWF", "Trinity_R_Basin", [startCal.getTime()], 800, 600, ["Conservation Pool (static)"], "../headless/generateAllForBasin/test_%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png")

    print "Demonstrating a call to generateAllBasinPieImagesForGroup"
    generateAllBasinPieImagesForGroup("SWF", "XYZ", [startCal.getTime()], 800, 600, ["Conservation Pool (static)"], "../headless/generateAllForGroup/test_%office_id%_%basin_id%_%location_id%_%chart_template_id%_%date%.png")


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

# basinPie.generateBasinPieImage("SWF", "RSRT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/basin.jpg")

# basinPie.generateBasinPieImage("SWF", "Basin-Trinity_R_Basin", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/Basin-Trinity_R_Basin.png")
# basinPie.generateBasinPieImage("SWF", "W_Fork_Triniy_R", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/W_Fork_Triniy_R.png")
# basinPie.generateBasinPieImage("SWF", "Mountain_Ck", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/Mountain_Ck.png")
# basinPie.generateBasinPieImage("SWF", "GPAT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/GPAT2.png")
# basinPie.generateBasinPieImage("SWF", "GPET2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/GPET2.png")
# basinPie.generateBasinPieImage("SWF", "JPLT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/JPLT2.png")
# basinPie.generateBasinPieImage("SWF", "GPRT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/GPRT2.png")
# basinPie.generateBasinPieImage("SWF", "TGXT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/TGXT2.png")
# basinPie.generateBasinPieImage("SWF", "FWOT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/FWOT2.png")
# basinPie.generateBasinPieImage("SWF", "Clear_Fk_Trinity", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/Clear_Fk_Trinity.png")
# basinPie.generateBasinPieImage("SWF", "FWHT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/FWHT2.png")
# basinPie.generateBasinPieImage("SWF", "CFBT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/CFBT2.png")
# basinPie.generateBasinPieImage("SWF", "BNBT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/BNBT2.png")
# basinPie.generateBasinPieImage("SWF", "ADOT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/ADOT2.png")
# basinPie.generateBasinPieImage("SWF", "WEAT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/WEAT2.png")
# basinPie.generateBasinPieImage("SWF", "LWFT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/LWFT2.png")
# basinPie.generateBasinPieImage("SWF", "WFTT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/WFTT2.png")
# basinPie.generateBasinPieImage("SWF", "FLWT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/FLWT2.png")
# basinPie.generateBasinPieImage("SWF", "EAMT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/EAMT2.png")
# basinPie.generateBasinPieImage("SWF", "BOYT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/BOYT2.png")
# basinPie.generateBasinPieImage("SWF", "Big_Sandy_Cr", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/Big_Sandy_Cr.png")
# basinPie.generateBasinPieImage("SWF", "BRPT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/BRPT2.png")
# basinPie.generateBasinPieImage("SWF", "BCAT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/BCAT2.png")
# basinPie.generateBasinPieImage("SWF", "BPRT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/BPRT2.png")
# basinPie.generateBasinPieImage("SWF", "Elm_Fk", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/Elm_Fk.png")
# basinPie.generateBasinPieImage("SWF", "CART2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/CART2.png")
# basinPie.generateBasinPieImage("SWF", "Denton_Crk", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/Denton_Crk.png")
# basinPie.generateBasinPieImage("SWF", "DCGT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/DCGT2.png")
# basinPie.generateBasinPieImage("SWF", "GPVT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/GPVT2.png")
# basinPie.generateBasinPieImage("SWF", "EFLT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/EFLT2.png")
# basinPie.generateBasinPieImage("SWF", "LEWT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/LEWT2.png")
# basinPie.generateBasinPieImage("SWF", "RRLT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/RRLT2.png")
# basinPie.generateBasinPieImage("SWF", "DALT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/DALT2.png")
# basinPie.generateBasinPieImage("SWF", "TRDT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/TRDT2.png")
# basinPie.generateBasinPieImage("SWF", "E_Fork", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/E_Fork.png")
# basinPie.generateBasinPieImage("SWF", "CNLT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/CNLT2.png")
# basinPie.generateBasinPieImage("SWF", "FNYT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/FNYT2.png")
# basinPie.generateBasinPieImage("SWF", "FRHT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/FRHT2.png")
# basinPie.generateBasinPieImage("SWF", "LVNT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/LVNT2.png")
# basinPie.generateBasinPieImage("SWF", "RSRT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/RSRT2.png")
# basinPie.generateBasinPieImage("SWF", "TDDT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/TDDT2.png")
# basinPie.generateBasinPieImage("SWF", "Richland_Ck", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/Richland_Ck.png")
# basinPie.generateBasinPieImage("SWF", "TRNT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/TRNT2.png")
# basinPie.generateBasinPieImage("SWF", "Chambers_Ck", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/Chambers_Ck.png")
# basinPie.generateBasinPieImage("SWF", "BRDT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/BRDT2.png")
# basinPie.generateBasinPieImage("SWF", "BDWT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/BDWT2.png")
# basinPie.generateBasinPieImage("SWF", "DWST2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/DWST2.png")
# basinPie.generateBasinPieImage("SWF", "DAWT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/DAWT2.png")
# basinPie.generateBasinPieImage("SWF", "LOLT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/LOLT2.png")

# basinPie.generateBasinPieImage("SWF", "LOLT2", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/test_%office%_LOLT2.png")

# basinPie.generateBasinPieImage("SWF", ["LOLT2","DAWT2"], "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/")
# basinPie.generateBasinPieImagesForBasin("SWF", "Trinity_R_Basin", startCal.getTime(), 800, 600, "Conservation Pool (static)", "../headless/")

if __name__ == "__builtin__":
    Usage()
    headless_examples()

if __name__ == "__main__":
    Usage()
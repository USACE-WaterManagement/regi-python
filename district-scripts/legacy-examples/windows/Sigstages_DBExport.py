sigstages = registry.getCalculation(1.0, "Export Sig States")

#sigstages has the following API exposed:
#
#    public void exportSigStages(String file);

# Purpose:
# Sigstages_DBExport.py retrieves information from the SWF database
# and writes the handbook_5 code for each location to a .txt file
# this file is read later by Sigstages_Download.py

outpath = "sites.txt"
sigstages.exportSigStages(outpath)
# Python Script Locations

## /district scripts
Scripts provided by the districts.  These are currently running and actively used by their associated districts.

- SWF Scripts were provided by James Moffitt
- SWT Scripts were provided by Andrew Miller
- SWL Scripts were provided by Erin Krebs

## /regi-headless/src/test/resources/usace/rowcps/headless/examples
These appear to be older example scripts that haven't been updated since 2019.  They are out of sync with other scripts.

## /regi-headless/src/test/resources/usace/rowcps/headless/tests
These appear to be older test scripts that haven't been updated since 2019.  They are out of sync with other scripts.

## /regi-headless-installer-windows/RegiHeadless/examples
These scripts and bash files are provided to the Solaris installer to provide an example of how to use regi-headless.  The scripts are slightly different from the Windows installer scripts, and the bash files are specifically for Solaris.

## /regi-headless-installer-solaris/RegiHeadless/examples
These scripts and batch files are provided to the Windows installer to provide an example of how to use regi-headless.  The scripts are slightly different from the Solaris installer scripts, and the batch files are specifically for Windows.

## Recommendations
1. Remove the /regi-headless/src/test/resources/usace/rowcps/headless/examples and /regi-headless/src/test/resources/usace/rowcps/headless/tests directories.
2. Consolidate Solaris and Windows python scripts to reduce maintenance and improve consistency across platforms.
3. Update python files to be compatible with the latest Python version.
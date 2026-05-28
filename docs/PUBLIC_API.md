# ScriptableCalc Public API

This document lists the public API for implementations of `ScriptableCalc`. These classes provide scriptable interfaces for various calculation and data management tasks within the REGI environment.

## Common Base: AbstractScriptableCalc
Most implementations inherit from `AbstractScriptableCalc`, which provides access to core domain objects.

- `getRegiDomain()`: Returns the `RegiDomain` instance associated with this calculator.
- `getManagerId()`: Returns the `ManagerId` identifying the user or session.
- `getManagerIdProvider()`: Returns a provider for the `ManagerId`.
- `getRegiTimeZone()`: Returns the `TimeZone` of the current `RegiDomain`.

---

## Implementations

### ScriptableExportTSAssociationsImpl
Handles exporting time series associations. (Found usages in `/regi-headless/src/test/resources/usace/rowcps/headless/examples`)

- `exportAllTSAssociations(String fileLoc, String lineDelimiter, String valueDelimiter)`: Exports all time series associations for all projects to the specified file.
- `exportTSAssociations(String projectId, String fileLoc, String lineDelimiter, String valueDelimiter)`: Exports time series associations for a specific project to the specified file.

### ScriptableExportSigStagesImpl
Handles exporting significant stages to a file.

- `exportSigStages(String file)`: Exports significant stages to the specified file path.
- `setOffice(String office)`: Sets the office ID to be used for the export.
- `getOffice()`: Returns the current office ID.

### ScriptableImportSigStagesImpl
Handles importing significant stages from a file.

- `importSigStages(String file, Date effectiveDate)`: Imports significant stages from the specified file, using the provided effective date.

### RetrieveSigStagesImpl
Retrieves significant stages from external sources and writes them to CSV.

- `retrieveSigstages(String sourceFile, String outputFile, int milliDelay)`: Reads NWS names from a source file and writes retrieved stages to an output file with a specified delay between requests.
- `setCSVHeader(String csvHeader)`: Sets a custom header for the generated CSV file.
- `getCSVHeader()`: Returns the current CSV header string.
- `setParameter(String parameter)`: Sets the parameter name for retrieval (e.g., Stage).
- `getParameter()`: Returns the current parameter name.
- `setParameterType(String parameterType)`: Sets the parameter type (e.g., Inst).
- `getParameterType()`: Returns the current parameter type.
- `setDuration(String duration)`: Sets the duration for retrieval (e.g., 0).
- `getDuration()`: Returns the current duration.
- `setOffice(String office)`: Sets the office ID for retrieval.
- `getOffice()`: Returns the current office ID.
- `setSpecifiedLevelOverride(Type type, String overrideText)`: Sets an override for a specific level type.
- `getSpecifiedLevelOverride(Type type)`: Returns the override text for a specific level type.

### ScriptableGateFlowImpl
Computes gate flows for locations. Found usages in `/district scripts`.

- `computeAll(String officeId, String locationId, Date start, Date end)`: Computes all gate flows for a location within the specified date range. (Used in scripts)
- `computeAll(String officeId, String[] locationIds, Date start, Date end)`: Computes all gate flows for multiple locations within the specified date range.
- `computeFlowGroup(String officeId, String locationId, Date start, Date end, String groupId)`: Computes gate flows for a specific group at a location. (Used in scripts)
- `computeFlowGroup(String officeId, String[] locationIds, Date start, Date end, String groupId)`: Computes gate flows for a specific group across multiple locations.

### ScriptableGateSettingsImpl
Manages and creates gate settings. Found usages in `/district scripts`.

- `createGateSettings(String officeId, String locationStr, Date startDate, Date end)`: Creates gate settings for all outlets at a location.
- `createGateSettingsOutlet(String officeId, String locationStr, Date startDate, Date end, String outletId)`: Creates gate settings for a specific outlet.
- `createGateSettingsOutletFromTs(String officeId, String locationStr, Date startDate, Date end, String outletId, String tsId)`: Creates gate settings for an outlet using a specific time series as input. (Used in scripts)
- `createGateSettingsGroup(String officeId, String locationStr, Date startDate, Date end, String groupId)`: Creates gate settings for a specific group of outlets.

### ScriptableInflowImpl
Handles inflow calculations and adjustments. Found usages in `/district scripts`.

- `autoAdjust(String officeId, String locationStr, Date startDate)`: Automatically adjusts inflows starting from the specified date.
- `autoAdjust(String officeId, String locationStr, Date startDate, boolean useLimits, boolean freezeRain)`: Automatically adjusts inflows with optional limits and rain freezing.
- `cloneInflows(String officeId, String locationStr, Date startDate)`: Clones inflows at a location starting from the specified date.
- `zeroNegatives(String officeId, String locationStr, Date startDate)`: Sets negative inflow values to zero starting from the specified date.
- `balanceAll(String officeId, String locationStr, Date startDate)`: Balances all inflows for a location starting from the specified date.
- `computeEvapAsFlow(String officeId, String locationStr, Date startDate, Date endDate)`: Computes evaporation as flow for the specified period. (Used in scripts)
- `computeInflow(String officeId, String locationStr, Date startDate, Date endDate)`: Computes inflow for the specified location and period. (Used in scripts)
- `setComputationStorageOptions(InflowComputationStorageOption option, InflowComputationStorageOption... options)`: Sets storage options for inflow computations. (Used in scripts)

### ScriptablePoolPercentImpl
Calculates pool percentage time series.

- `calculatePoolPercents(String officeId, String locationStr, Date startDate, Date endDate)`: Calculates pool percentages for a location within the specified date range.
- `retrieveDefaultTsId(RegiPool pool)`: Retrieves the default time series ID mask for a given pool.

### ScriptableStatusGraphicImpl
Generates status graphic images for reservoirs, streams, and releases.

- `generateReservoirStatusImage(String officeId, String locationId, String templateName, Date current, int width, int height, String filename)`: Generates a reservoir status image.
- `generateStreamStatusImage(String officeId, String locationId, String templateName, Date current, int width, int height, String filename)`: Generates a stream status image.
- `generateReleasesStatusImage(String officeId, String locationId, String templateName, Date current, int width, int height, String filename)`: Generates a releases status image.
- `generateBasinPieImageForGroup(String officeId, String locationStr, String groupId, Date date, int width, int height, String template, String file)`: Generates a basin pie chart image for a specific group.
- `generateBasinPieImageForBasin(String officeId, String locationStr, String basinId, Date date, int width, int height, String template, String file)`: Generates a basin pie chart image for a specific basin.
- `generateAllBasinPieImagesForBasin(String officeId, String basinId, Date[] dates, int width, int height, String[] templateIds, String file)`: Generates basin pie images for all dates and templates for a basin.
- `generateAllBasinPieImagesForGroup(String officeId, String groupId, Date[] dates, int width, int height, String[] templateIds, String file)`: Generates basin pie images for all dates and templates for a group.
- `getMapTemplates()`: Returns a list of available map templates.
- `getMapTemplateLayer(String templateName)`: Returns a specific map template layer by name.

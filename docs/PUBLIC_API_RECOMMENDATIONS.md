# Java API Recommendations

## Definitions
- Recent Examples are located in `/regi-headless-installer-solaris/RegiHeadless-Solaris/examples` and `/regi-headless-installer-windows/RegiHeadless/examples`
  - The most up to date and recent examples
- District Scripts are located in `/district scripts`
  - Scripts currently in use by the USACE Districts
- Older Examples are located in `/regi-headless/src/test/resources/usace/rowcps/headless/examples` and `/regi-headless/src/test/resources/usace/rowcps/headless/tests`
  - Older scripts used as examples, but have not been updated since 2019.  See `SCRIPT_RECOMMENDATIONS.md` for more information.

## Public API Recommendations
### Public API Removal Recommendations
| Classes                                | Description                                                     | Used in recent Examples | Used in District Scripts | Used in older Examples | Recommended for Removal | Notes          |
|----------------------------------------|-----------------------------------------------------------------|-------------------------|--------------------------|------------------------|-------------------------|----------------|
| **ScriptableExportTSAssociationsImpl** | [Description](PUBLIC_API.md#scriptableexporttsassociationsimpl) | No                      | No                       | Yes                    | Yes                     | Unused calc    |
| **ScriptableExportSigStagesImpl**      | [Description](PUBLIC_API.md#scriptableexportsigstagesimpl)      | Yes                     | No                       | Yes                    | Yes                     | Unused calc    |
| **ScriptableImportSigStagesImpl**      | [Description](PUBLIC_API.md#scriptableimportsigstagesimpl)      | Yes                     | No                       | Yes                    | Yes                     | Unused calc    |
| **RetrieveSigStagesImpl**              | [Description](PUBLIC_API.md#retrievesigstagesimpl)              | Yes                     | No                       | Yes                    | Yes                     | Unused calc    |
| **ScriptableGateFlowImpl**             | [Description](PUBLIC_API.md#scriptablegateflowimpl)             | Yes                     | Yes                      | Yes                    | No                      |                |
| **ScriptableGateSettingsImpl**         | [Description](PUBLIC_API.md#scriptablegatesettingsimpl)         | Yes                     | Yes                      | Yes                    | No                      |                |
| **ScriptableInflowImpl**               | [Description](PUBLIC_API.md#scriptableinflowimpl)               | Yes                     | Yes                      | Yes                    | No                      |                |
| **ScriptablePoolPercentImpl**          | [Description](PUBLIC_API.md#scriptablepoolpercentimpl)          | Yes                     | No                       | Yes                    | Yes                     | Being replaced |
| **ScriptableStatusGraphicImpl**        | [Description](PUBLIC_API.md#scriptablestatusgraphicimpl)        | Yes                     | No                       | Yes                    | Yes                     | Being replaced |

### Public API Changes

#### ScriptableInflowImpl
See [ScriptableInflowImpl](PUBLIC_API.md#scriptableinflowimpl)

| Method                                                                                            | Used in recent Examples | Used in District Scripts | Used in older Examples | Recommended for Removal | Notes                                                                           |
|---------------------------------------------------------------------------------------------------|-------------------------|--------------------------|------------------------|-------------------------|---------------------------------------------------------------------------------|
| `autoAdjust(String officeId, String locationStr, Date startDate)`                                                                | Yes                     | Yes                      | Yes                    | No                      |                                                                                 |
| `autoAdjust(String officeId, String locationStr, Date startDate, boolean useLimits, boolean freezeRain)`               | No                      | No                       | No                     | Maybe                   | Unused overload. Default: `useLimits=false`, `freezeRain=false`                 |
| `cloneInflows(String officeId, String locationStr, Date startDate)`                                                              | Yes                     | Yes                      | Yes                    | No                      |                                                                                 |
| `zeroNegatives(String officeId, String locationStr, Date startDate)`                                                             | Yes                     | Yes                      | Yes                    | No                      |                                                                                 |
| `balanceAll(String officeId, String locationStr, Date startDate)`                                                                | Yes                     | Yes                      | Yes                    | No                      |                                                                                 |
| `computeEvapAsFlow(String officeId, String locationStr, Date startDate, Date endDate)`                                                   | Yes                     | Yes                      | Yes                    | No                      |                                                                                 |
| `computeInflow(String officeId, String locationStr, Date startDate, Date endDate)`                                                       | Yes                     | Yes                      | Yes                    | No                      |                                                                                 |
| `setComputationStorageOptions(InflowComputationStorageOption option, InflowComputationStorageOption... options)` | No                      | No                       | No                     | Yes                     | **Unsupported.** Throws `UnsupportedOperationException`. See PUBLIC_API.md docs |

#### **ScriptableGateSettingsImpl**
See [ScriptableGateSettingsImpl](PUBLIC_API.md#scriptablegatesettingsimpl)

| Method                                                                       | Used in recent Examples | Used in District Scripts | Used in older Examples | Recommended for Removal | Notes                                                     |
|------------------------------------------------------------------------------|-------------------------|--------------------------|------------------------|-------------------------|-----------------------------------------------------------|
| `createGateSettings(String officeId, String locationStr, Date startDate, Date end)`                             | Yes                     | No                       | Yes                    | Maybe                   | Unused by District Scripts, may want to consider removing |
| `createGateSettingsOutlet(String officeId, String locationStr, Date startDate, Date end, String outletId)`               | Yes                     | Yes                      | Yes                    | No                      |                                                           |
| `createGateSettingsOutletFromTs(String officeId, String locationStr, Date startDate, Date end, String outletId, String tsId)` | Yes                     | Yes                      | Yes                    | No                      |                                                           |
| `createGateSettingsGroup(String officeId, String locationStr, Date startDate, Date end, String groupId)`                | Yes                     | No                       | Yes                    | Maybe                   | Unused by District Scripts, may want to consider removing |

#### **ScriptableGateFlowImpl**
See [ScriptableGateFlowImpl](PUBLIC_API.md#scriptablegateflowimpl)

| Method                                                   | Used in recent Examples | Used in District Scripts | Used in older Examples | Recommended for Removal | Notes           |
|----------------------------------------------------------|-------------------------|--------------------------|------------------------|-----------------------|-----------------|
| `computeAll(String officeId, String locationId, Date start, Date end)`                 | Yes                     | Yes                      | Yes                    | No                    |                 |
| `computeAll(String officeId, String locationId, long startTime, long endTime)`               | No                      | No                       | No                     | Yes                   | Unused overload |
| `computeAll(String officeId, String[] locationIds, Date start, Date end)`               | No                      | No                       | No                     | Maybe                 | Unused overload |
| `computeAll(String officeId, String[] locationIds, long startTime, long endTime)`             | No                      | No                       | No                     | Yes                   | Unused overload |
| `computeFlowGroup(String officeId, String locationId, Date start, Date end, String groupId)`   | Yes                     | Yes                      | Yes                    | No                    |                 |
| `computeFlowGroup(String officeId, String locationId, long startTime, long endTime, String groupId)` | No                | No                       | No                     | Yes                   | Unused overload |
| `computeFlowGroup(String officeId, String[] locationIds, Date start, Date end, String groupId)` | No                      | No                       | No                     | No                    | Unused overload |
| `computeFlowGroup(String officeId, String[] locationIds, long startTime, long endTime, String groupId)` | No             | No                       | No                     | Yes                      | Unused overload |
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
| Classes                                | Used in recent Examples | Used in District Scripts | Used in older Examples | Recommended for Removal | Notes          |
|----------------------------------------|-------------------------|--------------------------|------------------------|-------------------------|----------------|
| **ScriptableExportTSAssociationsImpl** | No                      | No                       | Yes                    | Yes                     | Unused calc    |
| **ScriptableExportSigStagesImpl**      | Yes                     | No                       | Yes                    | Yes                     | Unused calc    |
| **ScriptableImportSigStagesImpl**      | Yes                     | No                       | Yes                    | Yes                     | Unused calc    |
| **RetrieveSigStagesImpl**              | Yes                     | No                       | Yes                    | Yes                     | Unused calc    |
| **ScriptableGateFlowImpl**             | Yes                     | Yes                      | Yes                    | No                      |                |
| **ScriptableGateSettingsImpl**         | Yes                     | Yes                      | Yes                    | No                      |                |
| **ScriptableInflowImpl**               | Yes                     | Yes                      | Yes                    | No                      |                |
| **ScriptablePoolPercentImpl**          | Yes                     | No                       | Yes                    | Yes                     | Being replaced |
| **ScriptableStatusGraphicImpl**        | Yes                     | No                       | Yes                    | Yes                     | Being replaced |

### Public API Changes

#### ScriptableInflowImpl
| Method                                                                                            | Used in recent Examples | Used in District Scripts | Used in older Examples | Recommended for Removal | Notes                                                |
|---------------------------------------------------------------------------------------------------|-------------------------|--------------------------|------------------------|-------------------------|------------------------------------------------------|
| `autoAdjust(String, String, Date)`                                                                | Yes                     | Yes                      | Yes                    | No                      |                                                      |
| `autoAdjust(String, String, Date, boolean, boolean)`                                              | No                      | No                       | No                     | Maybe                   | Unused overload                                      |
| `cloneInflows(String, String, Date)`                                                              | Yes                     | Yes                      | Yes                    | No                      |                                                      |
| `zeroNegatives(String, String, Date)`                                                             | Yes                     | Yes                      | Yes                    | No                      |                                                      |
| `balanceAll(String, String, Date)`                                                                | Yes                     | Yes                      | Yes                    | No                      |                                                      |
| `computeEvapAsFlow(String, String, Date, Date)`                                                   | Yes                     | Yes                      | Yes                    | No                      |                                                      |
| `computeInflow(String, String, Date, Date)`                                                       | Yes                     | Yes                      | Yes                    | No                      |                                                      |
| `setComputationStorageOptions(InflowComputationStorageOption, InflowComputationStorageOption...)` | No                      | No                       | No                     | Maybe                   | No longer used in recent scripts or District Scripts |

#### **ScriptableGateSettingsImpl**
| Method                                                                       | Used in recent Examples | Used in District Scripts | Used in older Examples | Recommended for Removal | Notes                                                     |
|------------------------------------------------------------------------------|-------------------------|--------------------------|------------------------|-------------------------|-----------------------------------------------------------|
| `createGateSettings(String, String, Date, Date)`                             | Yes                     | No                       | Yes                    | Maybe                   | Unused by District Scripts, may want to consider removing |
| `createGateSettingsOutlet(String, String, Date, Date, String)`               | Yes                     | Yes                      | Yes                    | No                      |                                                           |
| `createGateSettingsOutletFromTs(String, String, Date, Date, String, String)` | Yes                     | Yes                      | Yes                    | No                      |                                                           |
| `createGateSettingsGroup(String, String, Date, Date, String)`                | Yes                     | No                       | Yes                    | Maybe                   | Unused by District Scripts, may want to consider removing |

#### **ScriptableGateFlowImpl**
| Method                                                   | Used in recent Examples | Used in District Scripts | Used in older Examples | Recommended for Removal | Notes           |
|----------------------------------------------------------|-------------------------|--------------------------|------------------------|-------------------------|-----------------|
| `computeAll(String, String, Date, Date)`                 | Yes                     | Yes                      | Yes                    | No                      |                 |
| `computeAll(String, String[], Date, Date)`               | No                      | No                       | No                     | Maybe                   | Unused overload |
| `computeFlowGroup(String, String, Date, Date, String)`   | Yes                     | Yes                      | Yes                    | No                      |                 |
| `computeFlowGroup(String, String[], Date, Date, String)` | No                      | No                       | No                     | No                      | Unused overload |
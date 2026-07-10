from usace.rowcps.headless import LoggingOptions

# Description of: LoggingOptions.setDbMessageLevel(int level)
#
# Adds Time Series logging messages in the OracleTimeSeriesDaoImpl.  Recommended
# level is 2, as this provides basic information about the time series
# retrieval/storage.
#
# Message Level | Description
# --------------|-------------------------------------------------------------------------------------------------------------------------------|
# <=0           | Default value, does not do anything.  Lower values do not change behavior.                                                  |
# 1             | Logs message when no data is found.  Logs message when data is found, how much was retrieved or stored, and how long it took. |
# 2             | Adds message with name of time series, and the units to retrieve/store.                                                       |
# 3             | Adds message with the current time.                                                                                           |
# 4             | Adds message with first 10 dates and values from each time series.                                                            |
# >4            | Same as 4, but shows all values retrieved from each time series.  Higher values do not change behavior.                       |
# --------------|-------------------------------------------------------------------------------------------------------------------------------|

LoggingOptions.setDbMessageLevel(2)


# Description of: LoggingOptions.setMetricsEnabled(boolean value)
#
# Enables or disables the storage of REGI's Metric data pertaining to the
# performance of the application.  This is incredibly helpful for identifying
# issues where the application takes an excessive amount of time to operate.
#
# Metrics also log the location of the files as an INFO message if they are
# enabled.
#
# By default, Metrics are disabled.

LoggingOptions.setMetricsEnabled(True)

# Description of: LoggingOptions.enableAbridgedFlowGroupCompLogging()
#
# Enables the abridged flow group computation logging.  This only applies to flow group computations, and will log
# information similar to a non-verbose REGI computation log.
#
# Example Output:
# Flow Group: Gated_Total 30Jun2018 2400 CDT 90.00 (cfs)
#   Primary Time Series:	 SKIA.Flow-Controlled.Inst.1Hour.0.Rev-Regi-Flowgroup 	90.00 (cfs) 	External Time Series:	 none	Flow Group Computation:	 Total: 	90.00 (cfs)
#
# By default flow group computation logging is disabled.

LoggingOptions.enableAbridgedFlowGroupCompLogging()

# Description of: LoggingOptions.enableAbridgedFlowGroupCompLogging()
#
# Enables the full flow group computation logging.  This only applies to flow group computations, and will log
# information similar to a verbose REGI computation log.
#
# Example Output:
#   Primary Time Series:
#       TXKT2-Gated_Total.Flow-Out.Inst.1Hour.0.Rev-SWF-REGI 		87.00 (cfs) 				*	External Time Series:	 none	Flow Group Computation:	 Total: 	87.00 (cfs) 	| 	Merge Rule: 	Replace All	 Override Protection: 	false
#
#
#
# By default flow group computation logging is disabled.

LoggingOptions.enableFullFlowGroupCompLogging()

# Description of: LoggingOptions.disableFlowGroupCompLogging()
#
# Disables the logging of flow group computations.  This is the default state of the LoggingOptions and does not need
# to be called unless LoggingOptions.enableAbridgedFlowGroupCompLogging() or LoggingOptions.enableFullFlowGroupCompLogging()
# have been called.

LoggingOptions.disableFlowGroupCompLogging()
/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package usace.rowcps.headless;

import java.util.logging.Level;
import java.util.logging.Logger;
import usace.rowcps.headless.metrics.RegiHeadlessMetricsServiceProvider;
import usace.rowcps.metrics.RegiMetricsService;
import hec.db.cwms.DbiProperties;

/**
 *
 * @author ryanm
 */
public class LoggingOptions
{

	private static final Logger LOGGER = Logger.getLogger(LoggingOptions.class.getName());
	private static boolean _fullFlowGroupCompLoggingEnabled;
	private static boolean _flowGroupCompLoggingEnabled;
	
	private LoggingOptions()
	{
		throw new AssertionError("Instantiation of a utility class is not allowed.");
	}

    /**
     * Sets the DbiProperties message level so we're reporting additional DB
     * related messages.
     *
     * Valid values range from 0-6, values outside of this range act as either 0
     * or 6, because the messages generally look for &gt;5 and &lt;= 0.
     *
     * This should probably be put somewhere other than the RegiCalcRegistry,
     * but for now this works.
     *
     * @param messageLevel Message level, this is expected to be between 0 and 6.  Anything lower or higher will clamp
	 *                     to the minimum or maximum value.
     */
    public static void setDbMessageLevel(int messageLevel)
    {
        DbiProperties.setMessageLevel(messageLevel);
        LOGGER.log(Level.FINE, "Setting Db Message Level to: {0}", messageLevel);
    }

    /*
     * Enables or disables the storage of REGI's Metric data pertaining to the
     * performance of the application. This is incredibly helpful for
     * identifying issues where the application takes an excessive amount of
     * time to operate.
     *
     * Metrics also log the location of the files as an INFO message if they are
     * enabled. By default, Metrics are disabled.
     */
    public static void setMetricsEnabled(boolean enabled)
    {
        RegiHeadlessMetricsServiceProvider.setMetricsEnabled(enabled);

        if (enabled)
        {
            LOGGER.log(Level.INFO, "Metrics enabled, files can be found at {0}",
					RegiMetricsService.getMetricsConfig().getPreferredFileLocation());
        }
    }

	/**
	 * Checks if the flow group computation logging is enabled.  This is only used during flow group computations.
	 *
	 * @return True if logging is enabled, false if it is not enabled.
	 */
	public static boolean isFlowGroupCompLoggingEnabled()
	{
		return _flowGroupCompLoggingEnabled;
	}

	/**
	 * Checks if the abridged logging of flow group computations is enabled.  This also includes a check to
	 * isFlowGroupCompLoggingEnabled.
	 *
	 * @return True if logging is enabled and it's abridged logging.
	 */
    public static boolean isAbridgedFlowGroupCompLoggingEnabled()
	{
		return _flowGroupCompLoggingEnabled && !_fullFlowGroupCompLoggingEnabled;
	}

	/**
	 * Checks if the full logging of flow group computations is enabled.  This also includes a check to
	 * isFlowGroupCompLoggingEnabled.
	 *
	 * @return True if logging is enabled and it's full logging.
	 */
	public static boolean isFullFlowGroupCompLoggingEnabled()
	{
		return _flowGroupCompLoggingEnabled && _fullFlowGroupCompLoggingEnabled;
	}

	/**
	 * Enables logging of simplified flow group computation data.  This is the equivalent to unchecking verbose in REGI.
	 */
	public static void enableAbridgedFlowGroupCompLogging()
	{
		if (!isAbridgedFlowGroupCompLoggingEnabled())
		{
			_flowGroupCompLoggingEnabled = true;
			_fullFlowGroupCompLoggingEnabled = false;
			LOGGER.log(Level.INFO, "Abridged flow group computation logging enabled.");
		}
	}

	/**
	 * Enables logging of full flow group computation data.  This is equivalent to checking verbose in REGI.
	 */
    public static void enableFullFlowGroupCompLogging()
	{
		if (!isFullFlowGroupCompLoggingEnabled())
		{
			_flowGroupCompLoggingEnabled = true;
			_fullFlowGroupCompLoggingEnabled = true;
			LOGGER.log(Level.INFO, "Full flow group computation logging enabled.");
		}
	}

	/**
	 * Disables logging of flow group computations.  This is the default state of the flow group computation logging
	 * and is not required to be called
	 */
	public static void disableFlowGroupCompLogging()
	{
		if (isFlowGroupCompLoggingEnabled())
		{
			_flowGroupCompLoggingEnabled = false;
			LOGGER.info("Flow group computation logging is disabled");
		}
	}
}

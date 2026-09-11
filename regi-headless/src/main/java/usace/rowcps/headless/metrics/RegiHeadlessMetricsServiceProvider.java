/*
 * Copyright (c) 2018
 * United States Army Corps of Engineers - Hydrologic Engineering Center (USACE/HEC)
 * All Rights Reserved.  USACE PROPRIETARY/CONFIDENTIAL.
 * Source may not be released without written approval from HEC
 */

package usace.rowcps.headless.metrics;

import java.util.Properties;
import java.util.prefs.Preferences;
import org.openide.util.lookup.ServiceProvider;
import usace.rowcps.metrics.RegiMetricsServiceProvider;
import usace.metrics.services.MetricsServiceProvider;
import usace.metrics.services.MetricsService;
import usace.metrics.services.config.MetricsConfig;
import usace.metrics.services.config.MetricsConfigBuilder;

/**
 *
 * @author @author <a href="mailto:ryanm@rmanet.com">Ryan A. Miles (ryanm@rmanet.com)</a>
 */
@ServiceProvider(service = MetricsServiceProvider.class,
				 path = RegiMetricsServiceProvider.SERVICE_PATH,
				 position = RegiMetricsServiceProvider.SERVICE_POSITION - 200)
public class RegiHeadlessMetricsServiceProvider extends RegiMetricsServiceProvider
{

	private final Properties _runtimeOverrides = new Properties();
	private static RegiHeadlessMetricsServiceProvider _singleton;

	public RegiHeadlessMetricsServiceProvider()
	{
		if (_singleton != null)
		{
			throw new IllegalStateException("An additional headless metrics service provider has been created.");
		}
		
		_singleton = this;
	}
	
	public static void setMetricsEnabled(boolean enabled)
	{
		if (_singleton != null)
		{
			_singleton.setRuntimeMetricsEnabled(enabled);
		}
	}
	
	private void setRuntimeMetricsEnabled(boolean enabled)
	{
		_runtimeOverrides.setProperty(MetricsConfig.METRICS_ENABLED_PREF, Boolean.toString(enabled));
	}
	
	@Override
	protected MetricsService createMetricsInstance(Preferences prefs, String appName, String filePrefix)
	{
		//Adjust the configuration so that Preferences are not used, only the RegiTools config and the app config.
		Properties overrides = new Properties();
		overrides.setProperty(MetricsConfig.METRICS_FILE_PREFIX_PREF, filePrefix);
		overrides.setProperty(MetricsConfig.METRICS_FILE_LOCATION_PREF, appName);
		
		MetricsConfigBuilder builder = new MetricsConfigBuilder()
				.withPropertiesFile(overrides)
				.withPropertiesFile(_runtimeOverrides);
		
		Properties props = readConfigFileAsProperties(appName);
		if (props != null)
		{
			builder = builder.withPropertiesFile(props);
		}
		
		if (prefs != null)
		{
			builder.withPreferenceOptions(prefs);
		}
		
		MetricsConfig metricsConfig = builder.withSystemPropertyOptions().build();
		
		return new MetricsService(metricsConfig);
	}
}

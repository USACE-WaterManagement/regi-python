/*
 * Copyright (c) 2018
 * United States Army Corps of Engineers - Hydrologic Engineering Center (USACE/HEC)
 * All Rights Reserved.  USACE PROPRIETARY/CONFIDENTIAL.
 * Source may not be released without written approval from HEC
 */
package usace.rowcps.headless.metrics;

import java.nio.file.Path;
import java.nio.file.Paths;
import org.openide.util.lookup.ServiceProvider;
import usace.metrics.services.MetricsApp;
import usace.metrics.services.config.MetricsConfig;
import usace.rowcps.metrics.RegiMetricsService;
import usace.rowcps.regi.factories.RegiDomainFactory;

/**
 *
 * @author @author <a href="mailto:ryanm@rmanet.com">Ryan A. Miles (ryanm@rmanet.com)</a>
 */
@ServiceProvider(service = MetricsApp.class)
public class RegiHeadlessMetricsApp implements MetricsApp
{

	@Override
	public String getAppName()
	{
		return "REGI Headless";
	}

	@Override
	public Path getMetricsRootDirectory()
	{
		return Paths.get(RegiDomainFactory.getRegiBaseDir(), "Metrics");
	}

	@Override
	public boolean isMetricsEnabled()
	{
		return true;
	}

	@Override
	public MetricsConfig getAppConfig()
	{
		return RegiMetricsService.getMetricsConfig();
	}
}

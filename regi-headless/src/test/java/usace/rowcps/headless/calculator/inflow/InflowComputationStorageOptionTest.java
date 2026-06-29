/*
 * Copyright (c) 2018
 * United States Army Corps of Engineers - Hydrologic Engineering Center (USACE/HEC)
 * All Rights Reserved.  USACE PROPRIETARY/CONFIDENTIAL.
 * Source may not be released without written approval from HEC
 */
package usace.rowcps.headless.calculator.inflow;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import usace.rowcps.data.inflow.InflowDataType;

/**
 *
 * @author Ryan A. Miles (ryanm@rmanet.com)
 */
public class InflowComputationStorageOptionTest
{

	@Test
	public void validateUniqueInflowDataTypes()
	{
		List<InflowDataType> existingDataTypes = new ArrayList<>();
		List<InflowDataType> nonUniqueDataTypes = new ArrayList<>();
		for (InflowComputationStorageOption option : InflowComputationStorageOption.values())
		{
			if (existingDataTypes.contains(option.getDataType()))
			{
				nonUniqueDataTypes.add(option.getDataType());
			}
			else
			{
				existingDataTypes.add(option.getDataType());
			}
		}
		
		if (!nonUniqueDataTypes.isEmpty())
		{
			assertTrue(false, "Non unique data types found: " + nonUniqueDataTypes);
		}
	}
}

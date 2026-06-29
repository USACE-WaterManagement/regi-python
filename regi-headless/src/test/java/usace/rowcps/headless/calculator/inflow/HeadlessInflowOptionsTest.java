/*
 * Copyright (c) 2018
 * United States Army Corps of Engineers - Hydrologic Engineering Center (USACE/HEC)
 * All Rights Reserved.  USACE PROPRIETARY/CONFIDENTIAL.
 * Source may not be released without written approval from HEC
 */
package usace.rowcps.headless.calculator.inflow;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Arrays;
import org.junit.jupiter.api.Test;
import usace.rowcps.data.inflow.InflowDataType;

/**
 *
 * @author Ryan A. Miles (ryanm@rmanet.com)
 */
public class HeadlessInflowOptionsTest
{

	@Test
	public void testDefaultCtor()
	{
		//By default, we should not have extra data types to store.
		HeadlessInflowOptions options = new HeadlessInflowOptions();

		assertFalse(options.isComputedDataTypeStored(InflowDataType.ProjectEvapAsFlow));
		assertFalse(options.isComputedDataTypeStored(InflowDataType.AverageRelease));
	}

	@Test
	public void testOneOption()
	{
		HeadlessInflowOptions options = new HeadlessInflowOptions();
		options.setComputationStorageOptions(Arrays.asList(InflowComputationStorageOption.EVAP_AS_FLOW));

		assertTrue(options.isComputedDataTypeStored(InflowDataType.ProjectEvapAsFlow));
		assertFalse(options.isComputedDataTypeStored(InflowDataType.AverageRelease));
	}

	@Test
	public void testAllComps()
	{
		/*
		Any and all computations in InflowComputationStorageOption should return true if we add them all in
		Uniqueness is checked in InflowComputationStorageOptionTest
		 */
		HeadlessInflowOptions options = new HeadlessInflowOptions();
		options.setComputationStorageOptions(Arrays.asList(InflowComputationStorageOption.values()));

		for (InflowComputationStorageOption option : InflowComputationStorageOption.values())
		{
			assertTrue(options.isComputedDataTypeStored(option.getDataType()));
		}
	}

	@Test
	public void testDoubleSetCompOptions()
	{
		//setComputationStorageOptions should clear out the original values not add to them
		HeadlessInflowOptions options = new HeadlessInflowOptions();
		options.setComputationStorageOptions(Arrays.asList(InflowComputationStorageOption.EVAP_AS_FLOW));
		options.setComputationStorageOptions(Arrays.asList(InflowComputationStorageOption.PROJECT_RELEASES));

		assertFalse(options.isComputedDataTypeStored(InflowDataType.ProjectEvapAsFlow));
		assertTrue(options.isComputedDataTypeStored(InflowDataType.AverageRelease));
	}
}

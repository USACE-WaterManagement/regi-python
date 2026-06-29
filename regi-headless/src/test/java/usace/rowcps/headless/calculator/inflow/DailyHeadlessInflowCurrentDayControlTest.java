/*
 * Copyright (c) 2018
 * United States Army Corps of Engineers - Hydrologic Engineering Center (USACE/HEC)
 * All Rights Reserved.  USACE PROPRIETARY/CONFIDENTIAL.
 * Source may not be released without written approval from HEC
 */
package usace.rowcps.headless.calculator.inflow;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Calendar;
import java.util.Date;
import java.util.NavigableSet;
import java.util.TimeZone;
import java.util.logging.Logger;

import hec.data.DataSetException;
import hec.data.location.LocationTemplate;
import hec.data.tx.DataSetTxIllegalArgumentException;
import hec.db.DbConnectionException;
import hec.db.DbException;
import hec.db.DbIoException;
import org.junit.jupiter.api.Test;
import usace.rowcps.regi.executor.ManagerIdType;
import usace.rowcps.regi.model.ManagerId;

/**
 *
 * @author Ryan A. Miles (ryanm@rmanet.com)
 */
public class DailyHeadlessInflowCurrentDayControlTest
{

	private static final Logger LOGGER = Logger.getLogger(DailyHeadlessInflowCurrentDayControlTest.class.getName());

	private Date getEndDate(Calendar temp)
	{
		temp.clear();
		temp.set(Calendar.YEAR, 2018);
		temp.set(Calendar.MONTH, 4);
		temp.set(Calendar.DAY_OF_MONTH, 7);

		return temp.getTime();
	}

	private Date getEndDateApr(Calendar temp)
	{
		temp.clear();
		temp.set(Calendar.YEAR, 2018);
		temp.set(Calendar.MONTH, 5);
		temp.set(Calendar.DAY_OF_MONTH, 7);

		return temp.getTime();
	}

	private Date getStartDate(Calendar temp)
	{
		temp.clear();
		temp.set(Calendar.YEAR, 2018);
		temp.set(Calendar.MONTH, 4);

		return temp.getTime();
	}

	private Date getExpectedStartDate(Calendar temp, Date startDate)
	{
		temp.setTime(startDate);
		temp.add(Calendar.DAY_OF_MONTH, 1);

		return temp.getTime();
	}

	//23-001 - migration
//	@Test
	public void testBaseCaseStartDate() throws Exception
	{
		TimeZone timeZone = TimeZone.getTimeZone("US/Central");
		Calendar temp = Calendar.getInstance(timeZone);
		Date endDate = getEndDate(temp);
		testStartDateIsMaintained(temp, endDate);
	}

	@Test
	public void testBaseCaseEndDate() throws Exception
	{
		TimeZone timeZone = TimeZone.getTimeZone("US/Central");
		Calendar temp = Calendar.getInstance(timeZone);
		Date endDate = getEndDate(temp);
		testEndDate(temp, endDate);
	}

	@Test
	public void testElevDateAfterEndDate() throws Exception
	{
		TimeZone timeZone = TimeZone.getTimeZone("US/Central");
		Calendar temp = Calendar.getInstance(timeZone);
		getEndDate(temp);
		temp.add(Calendar.DAY_OF_MONTH, 2);
		Date afterEndDate = temp.getTime();
		testEndDate(temp, afterEndDate);
	}

	@Test
	public void testElevDateBeforeEndDate() throws Exception
	{
		TimeZone timeZone = TimeZone.getTimeZone("US/Central");
		Calendar temp = Calendar.getInstance(timeZone);
		getEndDate(temp);
		temp.add(Calendar.DAY_OF_MONTH, -1);
		Date beforeEndDate = temp.getTime();
		testEndDate(temp, beforeEndDate);
	}

	@Test
	public void testEndDateCrossingMonthBarrier() throws Exception
	{
		TimeZone timeZone = TimeZone.getTimeZone("US/Central");
		Calendar temp = Calendar.getInstance(timeZone);
		Date endDate = getEndDateApr(temp);
		Date startDate = getStartDate(temp);
		testEndDateRespectsElevDate(startDate, endDate, endDate, temp);
	}

	//23-001 - migration
//	@Test
	public void testStartDateCrossingMonthBarrier() throws Exception
	{
		TimeZone timeZone = TimeZone.getTimeZone("US/Central");
		Calendar temp = Calendar.getInstance(timeZone);
		Date endDate = getEndDateApr(temp);
		Date startDate = getStartDate(temp);
		testStartDateIsMaintained(startDate, endDate, endDate, temp);
	}

	@Test
	public void testStartDateMiddleOfMonthCrossingMonthBarrier() throws Exception
	{
		TimeZone timeZone = TimeZone.getTimeZone("US/Central");
		Calendar temp = Calendar.getInstance(timeZone);
		Date endDate = getEndDateApr(temp);
		getStartDate(temp);
		temp.add(Calendar.DAY_OF_MONTH, -15);
		Date startDate = temp.getTime();
		testStartDateIsMaintained(startDate, endDate, endDate, temp);
	}

	private void testEndDate(Calendar temp, Date elevationDate) throws Exception
	{
		Date startDate = getStartDate(temp);
		Date endDate = getEndDate(temp);
		testEndDateRespectsElevDate(startDate, endDate, elevationDate, temp);
	}

	private void testStartDateIsMaintained(Calendar temp, Date elevationDate) throws Exception
	{
		Date startDate = getStartDate(temp);
		Date endDate = getEndDate(temp);
		testStartDateIsMaintained(startDate, endDate, elevationDate, temp);
	}

	private void testEndDateRespectsElevDate(Date startDate, Date endDate, Date elevationDate, Calendar temp) throws Exception
	{
		TestControl control = new TestControl(startDate, endDate)
		{
			@Override
			protected Date findLastElevDataDate(ManagerId manId, NavigableSet<Date> dates, LocationTemplate locRef) throws DbException, DbConnectionException, DbIoException, DataSetTxIllegalArgumentException, DataSetException
			{
				//This function normally serves as a data retrieval for elevation, so let's simulate that via elevationDate
				return elevationDate;
			}
		};
		LOGGER.severe(control.toString());

		Date expectedEndDate = elevationDate;

		if (elevationDate.after(endDate))
		{
			expectedEndDate = endDate;
		}

		Date controlEndDate = control.getEndDate(temp);
		assertEquals(expectedEndDate, controlEndDate);
	}

	private void testStartDateIsMaintained(Date startDate, Date endDate, Date elevationDate, Calendar temp) throws Exception
	{
		Date expectedStartDate = getExpectedStartDate(temp, startDate);
		TestControl control = new TestControl(startDate, endDate)
		{
			@Override
			protected Date findLastElevDataDate(ManagerId manId, NavigableSet<Date> dates, LocationTemplate locRef) throws DbException, DbConnectionException, DbIoException, DataSetTxIllegalArgumentException, DataSetException
			{
				//This is the only way I could get this in here...
				return elevationDate;
			}
		};
		LOGGER.severe(control.toString());
		assertEquals(expectedStartDate, control.getCurrentDate());
	}

	private class TestControl extends DailyHeadlessInflowCurrentDayControl
	{

		public TestControl(Date startDate, Date endDate) throws DbException, DbConnectionException, DbIoException, DataSetTxIllegalArgumentException, DataSetException
		{
			super(ManagerId.buildNewManagerId("", ManagerIdType.UNIT_TEST), startDate, endDate, TimeZone.getDefault(), new LocationTemplate());
		}

		Date getEndDate(Calendar temp)
		{
			Date controlDate = getCurrentDate();
			temp.setTime(controlDate);
			temp.add(Calendar.DAY_OF_MONTH, getLookForwardDays());
			return temp.getTime();
		}

		@Override
		public String toString()
		{
			StringBuilder sb = new StringBuilder("Dates:");
			for (Date date : getDates())
			{
				sb.append(System.lineSeparator()).append(date);
			}

			return sb.toString();
		}
	}
}

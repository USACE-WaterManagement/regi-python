/*
 * Copyright (c) 2018
 * United States Army Corps of Engineers - Hydrologic Engineering Center (USACE/HEC)
 * All Rights Reserved.  USACE PROPRIETARY/CONFIDENTIAL.
 * Source may not be released without written approval from HEC
 */
package usace.rowcps.headless;

import java.util.TimeZone;
import org.junit.jupiter.api.BeforeAll;
import usace.rowcps.cwms.Installer;
import usace.rowcps.headless.tests.TestVariables;

/**
 * This class is intended for use by developers to run headless after making changes. Run a single test at a time
 * otherwise it might be a while...
 * 
 * All files are relative to the JYTHON_FILE_ROOT variable, which should be in this same folder.
 *
 * @author @author <a href="mailto:ryanm@rmanet.com">Ryan A. Miles (ryanm@rmanet.com)</a>
 */
public class TestHeadless
{
	static final String JYTHON_FILE_ROOT = "src\\test\\java\\usace\\rowcps\\headless\\";
	static final String CREDENTIALS_FILE = "usace/rowcps/headless/credentials.properties";
	
	//I'd like this to be the office, but we haven't connected yet.
	//Could get it from the credentials probably.
	static final String SUB_FOLDER = "tests";
	
//	@Test //23-001 - migration
	public void testAssoc_DBExport() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("Assoc_DBExport.py"));
	}
	
//	@Test //23-001 - migration
	public void testBasinPieExport() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("BasinPieExport.py"));
	}
	
//	@Test //23-001 - migration
	public void testGateFlowPy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("GateFlow.py"));
	}
	
//	@Test //23-001 - migration
	public void testGateFlowCalcPy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("GateFlowCalc.py"));
	}

//	@Test //23-001 - migration
	public void testGateSettingsPy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("GateSettings.py"));
	}
	
//	@Test //23-001 - migration
	public void testInflowCalcAutoAdjustPy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("InflowCalcAutoAdjust.py"));
	}
	
//	@Test //23-001 - migration
	public void testInflowCalcBalanceAllPy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("InflowCalcBalanceAll.py"));
	}
	
//	@Test //23-001 - migration
	public void testInflowCalcClonePy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("InflowCalcClone.py"));
	}

//	@Test //23-001 - migration
	public void testInflowCalcComputeEvapAsFlowPy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("InflowCalcComputeEvapAsFlow.py"));
	}
	

//	@Test //23-001 - migration
	public void testInflowCalcComputedInflowPy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("InflowCalcComputedInflow.py"));
	}

//	@Test //23-001 - migration
	public void testInflowCalcZeroNegativePy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("InflowCalcZeroNegative.py"));
	}
	
//	@Test //23-001 - migration
	public void testPoolPercentCalcPy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("PoolPercentCalc.py"));
	}

//	@Test //23-001 - migration
	public void testSigstages_DBExportPy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("Sigstages_DBExport.py"));
	}

//	@Test //23-001 - migration
	public void testSigstages_DBImportPy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("Sigstages_DBImport.py"));
	}

//	@Test //23-001 - migration
	public void testSigstages_DownloadPy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("Sigstages_Download.py"));
	}

//	@Test //23-001 - migration
	public void testStatusDemoPy() throws Exception
	{
		RegiCLI.runHeadlessTest(getArgsForFile("StatusDemo.py"));
	}

	static String[] getArgsForFile(String file)
	{
		return getArgsForFileAndTimeZone(SUB_FOLDER + "\\" + file, TimeZone.getTimeZone("US/Central"));
	}
	
	static String getJythonTestFolder()
	{
		return JYTHON_FILE_ROOT + SUB_FOLDER;
	}

	private static String[] getArgsForFileAndTimeZone(String file, TimeZone tz)
	{
		TestVariables.init();
		String[] args = new String[]
		{
			"-Drowcps.timezone=" + tz.getID(),
			"-p", JYTHON_FILE_ROOT + CREDENTIALS_FILE,
			"-f", JYTHON_FILE_ROOT + file,
		};

		return args;
	}
	
	@BeforeAll
	public static void beforeClass()
	{
		//Sets up DB info
		Installer installer = new Installer();
		installer.restored();
	}
}

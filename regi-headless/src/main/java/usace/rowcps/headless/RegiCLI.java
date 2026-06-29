package usace.rowcps.headless;

import java.io.IOException;
import usace.rowcps.headless.interfaces.ScriptEvaluator;
import hec.db.DbConnectionException;
import hec.db.DbIoException;
import hec.db.DbPluginNotFoundException;
import hec.db.InvalidDbConnectionException;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.CmdLineParser;
import usace.rowcps.metrics.RegiMetricsService;
import usace.rowcps.regi.factories.RowcpsExecutorService;
import usace.rowcps.regi.model.ManagerId;
import usace.rowcps.regi.model.RegiDomain;
import usace.rowcps.regi.preferences.RegiPreferences;

/**
 *
 * @author ryan
 */
public class RegiCLI
{

	private static final Logger LOGGER = Logger.getLogger(RegiCLI.class.getName());

	static
	{
		RegiMetricsService.init(RegiPreferences.getClientNode().node("Metrics"), "REGI Headless");
	}

	public static void main(String[] args)
	{
		CLIOptions opt = new CLIOptions(System.getProperties());
		CmdLineParser parser = new CmdLineParser(opt);

		try
		{
			runHeadless(parser, args, opt);
		}
		catch (DbConnectionException | DbPluginNotFoundException | InvalidDbConnectionException | IOException ex)
		{
			LOGGER.log(Level.SEVERE, "Headless error connecting to database.", ex);
			System.exit(-1);
			return;
		}
		catch (CmdLineException | RuntimeException e)
		{
			LOGGER.log(Level.SEVERE, "Error running headless", e);
			System.err.println("java -jar myprogram.jar [options...] arguments...");
			parser.printUsage(System.err);
			System.exit(-1);
			return;
		}

		LOGGER.info("Exiting.");
		System.exit(0);
	}
	
	/**
	 * Used by TestHeadless unit test class to run headless without calling System.exit(0)
	 * 
	 * @param args
	 * @throws DbConnectionException
	 * @throws InvalidDbConnectionException
	 * @throws CmdLineException
	 * @throws DbPluginNotFoundException 
	 */
	static void runHeadlessTest(String[] args)
          throws DbConnectionException, InvalidDbConnectionException, CmdLineException, DbPluginNotFoundException,
          IOException {
		CLIOptions opt = new CLIOptions(System.getProperties());
		CmdLineParser parser = new CmdLineParser(opt);
		runHeadless(parser, args, opt);
	}

	private static void runHeadless(CmdLineParser parser, String[] args, CLIOptions opt)
          throws DbConnectionException, InvalidDbConnectionException, CmdLineException, DbPluginNotFoundException,
          IOException {
		parser.parseArgument(args);
		System.setProperties(opt.getProperties());
		
		HeadlessRegiDomainFactory factory = new HeadlessRegiDomainFactory();
		ManagerId managerId = factory.getManagerId();
		RegiDomain regiDomain = factory.createDomain();
		
		if (regiDomain != null)
		{
			ScriptEvaluator pe = new PythonEvaluator();
			Map<String, Object> vars = new HashMap<>();
			
			RegiCalcRegistry reg = new RegiCalcRegistry(regiDomain, managerId);
			vars.put("registry", reg);
			
			File scriptFile = opt.getScriptFile();
			
			try
			{
				FileReader fr = new FileReader(scriptFile);
				LOGGER.info("Evaluating script file");
				Object retval = pe.evaluateExpression(fr, vars);
				
				LOGGER.info("Jython script completed normally, commiting data.");
				regiDomain.commitData(managerId);
				LOGGER.info("RegiDomain committed data.");
			}
			catch (DbConnectionException | DbIoException | FileNotFoundException ex)
			{
				LOGGER.log(Level.SEVERE, "Exception occurred while evaluating Jython file:" + System.lineSeparator() + scriptFile, ex);
			}
			finally
			{
				LOGGER.info("RegiDomain closing.");
				shutdownRowcpsAccessFactory(managerId);
				regiDomain.closing();
			}
		}
	}

	private static void shutdownRowcpsAccessFactory(ManagerId managerId)
	{
		LOGGER.log(Level.INFO, "Shutting down RowcpsExecutorService for {0}", managerId);
		RowcpsExecutorService res = RowcpsExecutorService.getInstance(managerId);

		res.shutdown();  // signal shutdown - this will stop accepting new jobs and allow existing jobs to complete.
		boolean exitted = false;
		try
		{
			// We are willing to wait a little to achieve a clean shutdown.
			exitted = res.awaitTermination(3000, TimeUnit.MILLISECONDS);

		}
		catch (InterruptedException ie)
		{
			Thread.currentThread().interrupt();
		}
		if (!exitted)
		{
			// Some of the running tasks didn't exit in the time we were willing to wait.
			List<Runnable> wereWaiting = res.shutdownNow();  // This will interrupt them if they support interruption.
		}
		LOGGER.log(Level.INFO, "RowcpsExecutorService for {0} shutdown complete.", managerId);
	}
}

package usace.rowcps.headless;

import com.rma.io.RmaFile;
import com.rma.model.Project;
import hec.db.DataAccessFactory;
import hec.db.DbConnectionException;
import hec.db.DbIoException;
import hec.db.DbPluginNotFoundException;
import hec.db.cwms.CwmsSecurityDao;
import hec.lang.LoginException;
import hec.serversuite.ServerSuite;
import hec.serversuite.ServerSuiteUtil;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.logging.Level;
import java.util.logging.Logger;
import mil.army.usace.hec.serversuite.cda.CdaAuthenticationSource;
import mil.army.usace.hec.serversuite.cda.CwmsApiKeyAuthExtension;
import rma.services.ServiceLookup;
import rma.services.tz.TimeZoneDisplayService;
import usace.rowcps.regi.executor.ManagerIdType;
import usace.rowcps.regi.factories.RegiDomainFactory;
import usace.rowcps.regi.interfaces.model.ManagerIdProvider;
import usace.rowcps.regi.model.DatabaseConnectionManager;
import usace.rowcps.regi.model.ManagerId;
import usace.rowcps.regi.model.RegiDomain;

/**
 *
 * @author ryan
 */
public class HeadlessRegiDomainFactory
{

	private static final Logger logger = Logger.getLogger(HeadlessRegiDomainFactory.class.getName());
	private final ManagerIdProvider idProvider = buildNewProvider();

	public RegiDomain createDomain() throws DbConnectionException,
		DbPluginNotFoundException, IOException {

		Path projectDir = Paths.get("regi-projects", "regi-cli");
		logger.log(Level.INFO, "Creating project dir: "+ projectDir);
		Files.createDirectories(projectDir);

		Path projectFile = projectDir.resolve("regi-cli.prj");
		if(!Files.exists(projectFile)) {
			Files.createFile(projectFile);
		}

		Files.createDirectories(projectDir.resolve("reports"));
		Files.createDirectories(projectDir.resolve("xml"));

		String name = "Headless";
		String description = "Created for Headless execution.";
		RegiDomain regiDomain = new RegiDomainFactory().createProject(name, description, new RmaFile(projectFile.toAbsolutePath().toString()));

		regiDomain.loadProjectFile();

		DatabaseConnectionManager connectionManager = (DatabaseConnectionManager) regiDomain.getManager(
			RegiDomain.DOMAIN_CONNECTION_MANAGER, DatabaseConnectionManager.class);

		if (connectionManager == null) {
			connectionManager = regiDomain.buildDatabaseConnectionManager();
		}

		String cdaUrl = System.getenv("CDA_URL");
		String apiKey = System.getenv("API_KEY");
		String officeId = System.getenv("OFFICE_ID");

		CdaAuthenticationSource cdaAuthenticationSource = new CdaAuthenticationSource("", cdaUrl, officeId, new CwmsApiKeyAuthExtension(apiKey));
		try
		{
			ServerSuite serverSuite = ServerSuiteUtil.login("REGI CLI", cdaAuthenticationSource, false, false, false);
			DataAccessFactory dataAccessFactory = serverSuite.getDataAccessFactory();
			try(var key = dataAccessFactory.getDataAccessKey("REGI CLI")) {
				String username = dataAccessFactory.getDao(CwmsSecurityDao.class).getCurrentUserId(key);
				connectionManager.setUsername(username);
			}
			connectionManager.setTimeZoneId("UTC");
			connectionManager.setUserOfficeId(officeId);
			connectionManager.saveData();
			TimeZoneDisplayService tsDS = ServiceLookup.getTimeZoneDisplayService();
			tsDS.setTimeZone(connectionManager.getTimeZone());
			regiDomain.connect(ServerSuiteUtil.getServerSuite());
			//Resolve manager proxies to ensure they are initialized before saving the project
			regiDomain.getManagerList();
			regiDomain.saveProject();
			RegiDomain.setCurrentProject(regiDomain);
			Project.setCurrentProject(regiDomain);
			return regiDomain;
		}
		catch(LoginException | DbIoException ex)
		{
			throw new DbConnectionException(ex);
		}
	}

	public ManagerId getManagerId()
	{
		return idProvider.getManagerId();
	}


	private static ManagerIdProvider buildNewProvider()
	{
		return new ManagerIdProvider()
		{
			private final ManagerId _managerId = ManagerId.buildNewManagerId("Headless_" + System.currentTimeMillis(), ManagerIdType.HEADLESS);

			@Override
			public ManagerId getManagerId()
			{
				return _managerId;
			}

		};
	}

}

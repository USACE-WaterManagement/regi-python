package usace.rowcps.headless.calculator.inflow;

import hec.data.DataSetException;
import hec.data.location.LocationTemplate;
import hec.data.project.AtProjectDescriptor;
import hec.db.DbConnectionException;
import hec.db.DbException;
import hec.db.DbIoException;
import java.time.Instant;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.SortedMap;
import java.util.TimeZone;
import java.util.logging.Level;
import java.util.logging.Logger;
import usace.metrics.services.Metrics;
import usace.rowcps.computation.common.IntervalProvider;
import usace.rowcps.computation.inflow.BalanceAdjustedInflowsAction;
import usace.rowcps.computation.inflow.CloneInflowsAction;
import usace.rowcps.computation.inflow.InflowAdjustedTypeModel;
import usace.rowcps.computation.inflow.InflowCache;
import usace.rowcps.computation.inflow.InflowDataAdapter;
import usace.rowcps.computation.inflow.ZeroNegativeAdjustedInflowsAction;
import usace.rowcps.data.CacheInitializationException;
import usace.rowcps.data.inflow.InflowDataType;
import usace.rowcps.data.tabs.dailyops.GlobalDailyOpsOptionsBuilder;
import usace.rowcps.headless.calculator.AbstractScriptableCalc;
import usace.rowcps.headless.calculator.inflow.actions.HeadlessAutoAdjustInflowsAction;
import usace.rowcps.headless.calculator.inflow.actions.HeadlessBalanceAdjustedInflowsAction;
import usace.rowcps.headless.calculator.inflow.actions.HeadlessCloneInflowsAction;
import usace.rowcps.headless.calculator.inflow.actions.HeadlessZeroNegativeAdjustedInflowsAction;
import usace.rowcps.headless.interfaces.ScriptableCalc;
import usace.rowcps.metrics.RegiMetricsService;
import usace.rowcps.regi.model.CacheUsage;
import usace.rowcps.regi.model.ManagerId;
import usace.rowcps.regi.model.OptionalParams;
import usace.rowcps.regi.model.RegiDomain;
import usace.rowcps.regi.status.AtProjectManager;

/**
 *
 * @author ryan
 */
public class ScriptableInflowImpl extends AbstractScriptableCalc implements ScriptableCalc, ScriptableInflow
{

	private static final Logger LOGGER = Logger.getLogger(ScriptableInflowImpl.class.getName());

	private final long _msTimeOffsetIntoInterval = 7 * 3600 * 1000;  //TODO  7am for now
	private final String _intervalName = "1Day";
	private final Map<LocationTemplate, InflowAdjustedTypeModel> _statusMaps = new HashMap<>();
	private final HeadlessInflowOptions _options = new HeadlessInflowOptions();

	public ScriptableInflowImpl(RegiDomain regiDomain, ManagerId managerId)
	{
		super(regiDomain, managerId);
	}

	@Override
	public void autoAdjust(String officeId, String locationStr, Date startDate)
	{
		autoAdjust(officeId, locationStr, startDate, false, false);
	}

	@Override
	public void autoAdjust(String officeId, String locationStr, Instant startDate)
	{
		autoAdjust(officeId, locationStr, Date.from(startDate), false, false);
	}

	@Override
	public void autoAdjust(String officeId, String locationStr, Instant startDate, boolean useLimits, boolean freezeRain)
	{
		autoAdjust(officeId, locationStr, Date.from(startDate), useLimits, freezeRain);
	}

	@Override
	public void autoAdjust(String officeId, String locationStr, Date startDate, boolean useLimits, boolean freezeRain)
	{
		Metrics metrics = RegiMetricsService.createMetrics(getClass().getSimpleName(), "autoAdjust");
		OptionalParams options = new OptionalParams(metrics);

		LOGGER.info("Running ScriptableInflow.autoAdjust");
		LOGGER.log(Level.INFO, "\tofficeId: {0}", officeId);
		LOGGER.log(Level.INFO, "\tlocationStr: {0}", locationStr);
		LOGGER.log(Level.INFO, "\tstartDate: {0}", startDate);
		LOGGER.log(Level.INFO, "\tuseLimits: {0}", useLimits);
		LOGGER.log(Level.INFO, "\tfreezeRain: {0}", freezeRain);

		try
		{
			LocationTemplate locRef = new LocationTemplate(officeId, locationStr);

			InflowAdjustedTypeModel asm = getOrCreateStatusMap(locRef);

			InflowCache inflowCache = getInitializedMonthlyCache(locRef, startDate, options);
			startDate = inflowCache.getCeilingDateKey(startDate);

			LOGGER.info("performing AutoAdjustInflowsAction");

			HeadlessAutoAdjustInflowsAction aaia = new HeadlessAutoAdjustInflowsAction(startDate, inflowCache, hec.data.Units.ENGLISH_ID, asm);
			aaia.setFreezeRainDays(freezeRain);
			aaia.setUseLimits(useLimits);

			aaia.actionPerformed(null);
			LOGGER.info("AutoAdjustInflowsAction complete. Saving cache data.");

			inflowCache.saveData(options);

		}
		catch (DbConnectionException | DbIoException ex)
		{
			LOGGER.log(Level.SEVERE, "DB exception occurred while running autoAdjust", ex);
		}
		catch (InterruptedException ie)
		{
			Thread.currentThread().interrupt();
		}
		catch (Exception ex)
		{
			LOGGER.log(Level.SEVERE, "Exception occurred while running autoAdjust", ex);
		}
	}

	@Override
	public void cloneInflows(String officeId, String locationStr, Instant startDate)
	{
		cloneInflows(officeId, locationStr, Date.from(startDate));
	}

	@Override
	public void cloneInflows(String officeId, String locationStr, Date startDate)
	{
		Metrics metrics = RegiMetricsService.createMetrics(getClass().getSimpleName(), "cloneInflows");
		OptionalParams options = new OptionalParams(metrics);

		LOGGER.info("Running ScriptableInflow.cloneInflows");
		LOGGER.log(Level.INFO, "\tofficeId: {0}", officeId);
		LOGGER.log(Level.INFO, "\tlocationStr: {0}", locationStr);
		LOGGER.log(Level.INFO, "\tstartDate: {0}", startDate);

		try
		{
			LocationTemplate locRef = new LocationTemplate(officeId, locationStr);

			InflowAdjustedTypeModel asm = getOrCreateStatusMap(locRef);

			InflowCache inflowCache = getInitializedMonthlyCache(locRef, startDate, options);
			startDate = inflowCache.getCeilingDateKey(startDate);

			LOGGER.info("performing CloneInflowsAction");
			CloneInflowsAction cloneAction
					= new HeadlessCloneInflowsAction(startDate, inflowCache, hec.data.Units.ENGLISH_ID, asm);
			cloneAction.actionPerformed(null);
			LOGGER.info("CloneInflowsAction completed. Saving cache data.");

			inflowCache.saveData(options);

		}
		catch (DbConnectionException | DbIoException ex)
		{
			LOGGER.log(Level.SEVERE, "DB exception occurred while cloning inflows.", ex);
		}
		catch (Exception ex)
		{
			LOGGER.log(Level.SEVERE, "Unable to clone inflows", ex);
		}
	}

	@Override
	public void zeroNegatives(String officeId, String locationStr, Instant startDate)
	{
		zeroNegatives(officeId, locationStr, Date.from(startDate));
	}

	@Override
	public void zeroNegatives(String officeId, String locationStr, Date startDate)
	{
		Metrics metrics = RegiMetricsService.createMetrics(getClass().getSimpleName(), "zeroNegatives");
		OptionalParams options = new OptionalParams(metrics);

		LOGGER.info("Running ScriptableInflow.zeroNegatives");
		LOGGER.log(Level.INFO, "\tofficeId: {0}", officeId);
		LOGGER.log(Level.INFO, "\tlocationStr: {0}", locationStr);
		LOGGER.log(Level.INFO, "\tstartDate: {0}", startDate);

		try
		{
			LocationTemplate locRef = new LocationTemplate(officeId, locationStr);

			InflowAdjustedTypeModel asm = getOrCreateStatusMap(locRef);

			InflowCache inflowCache = getInitializedMonthlyCache(locRef, startDate, options);
			startDate = inflowCache.getCeilingDateKey(startDate);

			LOGGER.info("performing ZeroNegativeAdjustedInflowsAction");
			ZeroNegativeAdjustedInflowsAction zeroAction = new HeadlessZeroNegativeAdjustedInflowsAction(startDate, inflowCache,
					hec.data.Units.ENGLISH_ID, asm);
			zeroAction.actionPerformed(null);
			LOGGER.info("ZeroNegativeAdjustedInflowsAction complete.  Saving cache data.");
			inflowCache.saveData(options);

		}
		catch (DbConnectionException | DbIoException ex)
		{
			LOGGER.log(Level.SEVERE, "DB exception occured while zeroing negatives", ex);
		}
		catch (Exception ex)
		{
			LOGGER.log(Level.SEVERE, "Unable to zero negatives", ex);
		}
	}

	@Override
	public void balanceAll(String officeId, String locationStr, Instant startDate)
	{
		balanceAll(officeId, locationStr, Date.from(startDate));
	}

	@Override
	public void balanceAll(String officeId, String locationStr, Date startDate)
	{
		Metrics metrics = RegiMetricsService.createMetrics(getClass().getSimpleName(), "balanceAll");
		OptionalParams options = new OptionalParams(metrics);

		LOGGER.info("Running ScriptableInflow.balanceAll");
		LOGGER.log(Level.INFO, "\tofficeId: {0}", officeId);
		LOGGER.log(Level.INFO, "\tlocationStr: {0}", locationStr);
		LOGGER.log(Level.INFO, "\tstartDate: {0}", startDate);

		try
		{
			LocationTemplate locRef = new LocationTemplate(officeId, locationStr);

			InflowCache inflowCache = getInitializedMonthlyCache(locRef, startDate, options);
			startDate = inflowCache.getCeilingDateKey(startDate);

			InflowAdjustedTypeModel asm = getOrCreateStatusMap(locRef);

			LOGGER.info("performing BalanceAdjustedInflowsAction");
			BalanceAdjustedInflowsAction balanceAll = new HeadlessBalanceAdjustedInflowsAction(startDate, inflowCache,
					hec.data.Units.ENGLISH_ID, asm);
			balanceAll.actionPerformed(null);
			LOGGER.info("BalanceAdjustedInflowsAction complete.  Saving data.");

			inflowCache.saveData(options);

		}
		catch (DbConnectionException | DbIoException ex)
		{
			LOGGER.log(Level.SEVERE, "DB Exception occurred while balancing inflow", ex);
		}
		catch (Exception ex)
		{
			LOGGER.log(Level.SEVERE, "Unable to balance inflow", ex);
		}
	}

	private AtProjectDescriptor getProjectDescriptor(LocationTemplate template) throws DbConnectionException, DbIoException
	{
		RegiDomain domain = getRegiDomain();
		AtProjectManager atProjectManager = domain.getAtProjectManager(getManagerId());
		return atProjectManager.getProjectDescriptor(template, CacheUsage.NORMAL);
	}

	private TimeZone getProjectTimeZone(AtProjectDescriptor descriptor) throws DbConnectionException, DbIoException
	{
		RegiDomain domain = getRegiDomain();
		AtProjectManager atProjectManager = domain.getAtProjectManager(getManagerId());
		return atProjectManager.getIProject(descriptor).getProjectTimeZone();
	}

	private HeadlessInflowCache getInitializedDailyCache(LocationTemplate locRef, Date startDate, Date endDate, OptionalParams options)
			throws DbConnectionException, DbIoException, InterruptedException, CacheInitializationException, DbException, DataSetException
	{
		return getInitializedDailyCache(locRef, startDate, endDate, options, true);
	}
	
	private HeadlessInflowCache getInitializedDailyCache(LocationTemplate locRef, Date startDate, Date endDate, OptionalParams options, boolean retrieveAverageReleases)
			throws DbConnectionException, DbIoException, InterruptedException, CacheInitializationException, DbException, DataSetException
	{
		AtProjectDescriptor projectDescriptor = getProjectDescriptor(locRef);
		TimeZone projectTimeZone = getProjectTimeZone(projectDescriptor);
		DailyHeadlessInflowCurrentDayControl dayControl = new DailyHeadlessInflowCurrentDayControl(getManagerId(), startDate, endDate, projectTimeZone, locRef);

		return buildAndInitializeInflowCache(dayControl, projectDescriptor, projectTimeZone, startDate, options, retrieveAverageReleases);
	}

	private HeadlessInflowCache getInitializedMonthlyCache(LocationTemplate locRef, Date startDate, OptionalParams options)
			throws DbConnectionException, DbIoException, InterruptedException, CacheInitializationException, DbException, DataSetException
	{
		return getInitializedMonthlyCache(locRef, startDate, options, true);
	}
	
	private HeadlessInflowCache getInitializedMonthlyCache(LocationTemplate locRef, Date startDate, OptionalParams options, boolean retrieveAverageReleases)
			throws DbConnectionException, DbIoException, InterruptedException, CacheInitializationException, DbException, DataSetException
	{
		AtProjectDescriptor projectDescriptor = getProjectDescriptor(locRef);
		TimeZone projectTimeZone = getProjectTimeZone(projectDescriptor);
		MonthlyHeadlessInflowCurrentDayControl dayControl = new MonthlyHeadlessInflowCurrentDayControl(getManagerId(), startDate, projectTimeZone, locRef);

		return buildAndInitializeInflowCache(dayControl, projectDescriptor, projectTimeZone, startDate, options, retrieveAverageReleases);
	}
	
	private HeadlessInflowCache buildAndInitializeInflowCache(HeadlessInflowCurrentDayControl currentDayControl, AtProjectDescriptor projectDescriptor, TimeZone projectTimeZone, Date startDate, OptionalParams options, boolean retrieveAverageReleases) throws CacheInitializationException
	{
		InflowDataAdapter adapter;
		if (retrieveAverageReleases)
		{
			adapter = new InflowDataAdapter(projectDescriptor, getManagerId(), projectTimeZone, GlobalDailyOpsOptionsBuilder.buildDefaultOptions(projectDescriptor.getOfficeId()));
		}
		else
		{
			adapter = new HeadlessInflowDataAdapter(projectDescriptor, getManagerId(), projectTimeZone);
		}
		
		HeadlessInflowCache inflowCache = new HeadlessInflowCache(currentDayControl, getManagerId(), projectDescriptor,
				projectTimeZone, getIntervalProvider(projectTimeZone), adapter)
		{

			@Override
			protected void updateHeadTimeWindow(Calendar start, Calendar end, SortedMap<Date, ? extends Object> currentCache)
			{
				super.updateHeadTimeWindow(start, end, currentCache);
				if (start.getTime().after(startDate))
				{
					start.setTime(startDate);
				}
			}
		};

		inflowCache.waitForInitCache(options);

		LOGGER.info("InflowCache is initialized.");

		return inflowCache;
	}

	private IntervalProvider getIntervalProvider(TimeZone projectTimeZone)
	{
		return new HeadlessInflowIntervalProvider(_msTimeOffsetIntoInterval, projectTimeZone, _intervalName);
	}

	private InflowAdjustedTypeModel getOrCreateStatusMap(LocationTemplate template)
	{
		InflowAdjustedTypeModel retval = null;
		if (template != null)
		{
			retval = _statusMaps.computeIfAbsent(template, (t) -> new InflowAdjustedTypeModelImpl());
		}

		return retval;
	}

	@Override
	public void computeEvapAsFlow(String officeId, String locationStr, Instant startDate, Instant endDate)
	{
		computeEvapAsFlow(officeId, locationStr, Date.from(startDate), Date.from(endDate));
	}

	@Override
	public void computeEvapAsFlow(String officeId, String locationStr, Date startDate, Date endDate)
	{
		Metrics metrics = RegiMetricsService.createMetrics(getClass().getSimpleName(), "computeEvapAsFlow");
		OptionalParams options = new OptionalParams(metrics);

		LOGGER.info("Running ScriptableInflow.computeEvapAsFlow");
		LOGGER.log(Level.INFO, "\tofficeId: {0}", officeId);
		LOGGER.log(Level.INFO, "\tlocationStr: {0}", locationStr);
		LOGGER.log(Level.INFO, "\tstartDate: {0}", startDate);
		LOGGER.log(Level.INFO, "\tendDate: {0}", endDate);

		try
		{
			LocationTemplate locRef = new LocationTemplate(officeId, locationStr);
			HeadlessInflowCache cache = getInitializedDailyCache(locRef, startDate, endDate, options, false);

			cache.clearModifiedState();
			cache.setModifiedOnAllDataTypeValuesInTimeRange(InflowDataType.ProjectEvapAsFlow, true);

			cache.saveData(options);
		}
		catch (DbConnectionException | DbIoException ex)
		{
			LOGGER.log(Level.SEVERE, "DB Exception occurred while computing evap as flow", ex);
		}
		catch (Exception ex)
		{
			LOGGER.log(Level.SEVERE, "Unable to compute evap as flow", ex);
		}
	}

	@Override
	public void computeInflow(String officeId, String locationStr, Instant startDate, Instant endDate)
	{
		computeInflow(officeId, locationStr, Date.from(startDate), Date.from(endDate));
	}

	@Override
	public void computeInflow(String officeId, String locationStr, Date startDate, Date endDate)
	{
		Metrics metrics = RegiMetricsService.createMetrics(getClass().getSimpleName(), "computeInflow");
		OptionalParams options = new OptionalParams(metrics);

		LOGGER.info("Running ScriptableInflow.computeInflow");
		LOGGER.log(Level.INFO, "\tofficeId: {0}", officeId);
		LOGGER.log(Level.INFO, "\tlocationStr: {0}", locationStr);
		LOGGER.log(Level.INFO, "\tstartDate: {0}", startDate);
		LOGGER.log(Level.INFO, "\tendDate: {0}", endDate);

		try
		{
			LocationTemplate locRef = new LocationTemplate(officeId, locationStr);
			HeadlessInflowCache cache = getInitializedDailyCache(locRef, startDate, endDate, options);

			cache.clearModifiedState();
			cache.setModifiedOnAllDataTypeValuesInTimeRange(InflowDataType.ComputedInflow, true);
			cache.setModifiedOnAllDataTypeValuesInTimeRange(InflowDataType.ProjectEvapAsFlow, true);
			cache.setModifiedOnAllDataTypeValuesInTimeRange(InflowDataType.AverageRelease, true);

			cache.saveData(options);
		}
		catch (DbConnectionException | DbIoException ex)
		{
			LOGGER.log(Level.SEVERE, "DB Exception occurred while computing inflow", ex);
		}
		catch (Exception ex)
		{
			LOGGER.log(Level.SEVERE, "Unable to compute inflow", ex);
		}
	}

	@Override
	public void setComputationStorageOptions(InflowComputationStorageOption option, InflowComputationStorageOption ... options)
	{
		String msg = "setComputationStorageOptions function is no longer used.\n"
				   + "The computeInflow function will automatically save the following data:\n"
				   + "\tEvaporation as Flow\n"
				   + "\tAverage Releases\n"
				   + "\tDaily Computed Inflow\n";
		
		throw new UnsupportedOperationException(msg);
	}
}

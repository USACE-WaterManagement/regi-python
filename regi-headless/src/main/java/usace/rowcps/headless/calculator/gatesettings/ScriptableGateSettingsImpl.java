package usace.rowcps.headless.calculator.gatesettings;

import hec.data.DataObjectException;
import hec.data.DataSetException;
import hec.data.DataSetIllegalArgumentException;
import hec.data.Duration;
import hec.data.ITimeSeriesDescription;
import hec.data.Interval;
import hec.data.Parameter;
import hec.data.ParameterType;
import hec.data.Units;
import hec.data.UtcOffsetConst;
import hec.data.location.AssignedLocation;
import hec.data.location.Location;
import hec.data.location.LocationCategoryRef;
import hec.data.location.LocationGroup;
import hec.data.location.LocationGroupRef;
import hec.data.location.LocationGroupSet;
import hec.data.location.LocationTemplate;
import hec.data.outlet.IOutlet;
import hec.data.physicalstructure.IPhysicalStructure;
import hec.data.project.AtProjectDescriptor;
import hec.data.project.IProject;
import hec.data.tx.DataSetTx;
import hec.data.tx.DataSetTxIllegalArgumentException;
import hec.data.tx.DataSetTxTemplate;
import hec.data.tx.DescriptionTx;
import hec.db.DbConnectionException;
import hec.db.DbException;
import hec.db.DbIoException;
import hec.hecmath.HecMath;
import hec.hecmath.HecMathException;
import hec.hecmath.TimeSeriesMath;
import hec.io.TimeSeriesContainer;
import java.text.ChoiceFormat;
import java.text.Format;
import java.text.MessageFormat;
import java.text.NumberFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.NavigableMap;
import java.util.NavigableSet;
import java.util.Objects;
import java.util.Set;
import java.util.SortedSet;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.concurrent.ConcurrentNavigableMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;
import rma.util.RMAConst;
import usace.metrics.services.Metrics;
import usace.rowcps.computation.TimeSeriesIds;
import usace.rowcps.computation.common.grouping.IControlledOutlet;
import usace.rowcps.computation.common.grouping.IControlledOutletGroup;
import usace.rowcps.computation.common.grouping.IControlledOutletGroupContainer;
import usace.rowcps.computation.gatesettings.TimeSeriesDataContainer;
import usace.rowcps.computation.gatesettings.common.AggregateGateOpeningEntry;
import usace.rowcps.computation.gatesettings.common.DischargeComputationRecord;
import usace.rowcps.computation.gatesettings.common.DischargeComputationRecord.DischargeComputationCode;
import usace.rowcps.computation.gatesettings.common.GateCache;
import usace.rowcps.computation.gatesettings.common.GateMergeException;
import usace.rowcps.computation.gatesettings.common.GateOpeningEntry;
import usace.rowcps.computation.gatesettings.common.GateSettingsBlock;
import usace.rowcps.computation.gatesettings.finetuning.FineTuneRowElementSynthetic;
import usace.rowcps.computation.gatesettings.finetuning.FineTuningRowType;
import usace.rowcps.computation.util.LookupRecordBase;
import usace.rowcps.data.CacheInitializationException;
import usace.rowcps.data.InputOutput;
import usace.rowcps.data.association.IAssociationCatalog;
import usace.rowcps.data.association.IAssociationProvider;
import usace.rowcps.data.association.ITimeSeriesAssociation;
import usace.rowcps.data.project.TsUsageId;
import usace.rowcps.headless.calculator.AbstractScriptableCalc;
import usace.rowcps.headless.calculator.inflow.AbstractThreadedBlockRetriever;
import usace.rowcps.headless.interfaces.ScriptableCalc;
import usace.rowcps.metrics.RegiMetricsService;
import usace.rowcps.regi.event.IThreadedBlockRetriever;
import usace.rowcps.regi.executor.DefaultThreadIdProvider;
import usace.rowcps.regi.executor.ThreadIdProvider;
import usace.rowcps.regi.interfaces.model.ICurrentDayControl;
import usace.rowcps.regi.model.AtAssociationCache;
import usace.rowcps.regi.model.AtAssociationManager;
import usace.rowcps.regi.model.AtLocationGroupManager;
import usace.rowcps.regi.model.AtOutletManager;
import usace.rowcps.regi.model.AtRatingManager;
import usace.rowcps.regi.model.AtTimeSeriesManager;
import usace.rowcps.regi.model.CacheUsage;
import usace.rowcps.regi.model.ManagerId;
import usace.rowcps.regi.model.OptionalParams;
import usace.rowcps.regi.model.RegiDomain;
import usace.rowcps.regi.status.AtProjectManager;
import usace.rowcps.regi.util.GateSettingsUtil;

public class ScriptableGateSettingsImpl extends AbstractScriptableCalc implements ScriptableCalc, ScriptableGateSettings {

	private static final String LATCH_SECONDS = "rowcps.latchseconds";
	private static final Logger LOGGER = Logger.getLogger(ScriptableGateSettings.class.getName());

	public ScriptableGateSettingsImpl(RegiDomain regiDomain, ManagerId managerId) {
		super(regiDomain, managerId);
	}

	@Override
	public void createGateSettings(String officeId, String locationStr, Date startDate, Date end) throws Exception
	{
		Metrics metrics = RegiMetricsService.createMetrics(this.getClass().getSimpleName(), "createGateSettings");
		OptionalParams options = new OptionalParams(metrics);
		LocationTemplate locRef = new LocationTemplate(officeId, locationStr);
		HeadlessGateCache gc = getCache(locRef, startDate, end, options);

		String from = _simpleDateFormat.format(startDate);
		String to = _simpleDateFormat.format(end);
		LOGGER.log(Level.INFO, "Creating gate settings for all outlets at location using time series associations for " +
						"Office: {0} Location: {1} from: {2} to: {3}",
				new Object[]{officeId, locationStr, from, to});
		IControlledOutletGroupContainer outletGroupContainer = gc.getOutletGroupContainer();
		if(outletGroupContainer != null)
		{
			List<IControlledOutletGroup> outletGroups = outletGroupContainer.getOutletGroups();
			if(outletGroups != null && !outletGroups.isEmpty())
			{
				for(IControlledOutletGroup outletGroup : outletGroups)
				{
					createGateSettingsGroup(gc, locRef, startDate, end, outletGroup, options);
				}
			}
			else
			{
				LOGGER.log(Level.WARNING, "Gate settings not created. No outlet groups found for location: {0}", locationStr);
			}
		}
		gc.saveData(options);
	}

	@Override
	public void createGateSettingsOutlet(String officeId, String locationStr, Date startDate, Date end, String outletId) throws Exception
	{
		Metrics metrics = RegiMetricsService.createMetrics(this.getClass().getSimpleName(), "createGateSettingsOutlet");
		OptionalParams options = new OptionalParams(metrics);
		LocationTemplate locRef = new LocationTemplate(officeId, locationStr);
		HeadlessGateCache gc = getCache(locRef, startDate, end, options);

		IControlledOutlet iControlledOutlet = getIControlledOutlet(gc, outletId);
		String from = _simpleDateFormat.format(startDate);
		String to = _simpleDateFormat.format(end);
		LOGGER.log(Level.INFO, "Creating gate settings using time series associations for " +
						"Office: {0} Location: {1} Outlet: {2} from: {3} to: {4}",
				new Object[]{officeId, locationStr, outletId, from, to});
		if(iControlledOutlet != null)
		{
			ITimeSeriesAssociation association = getInputAssociation(locRef);
			Map<String, IOutlet> outletsBySubMap = getOutletsBySubMap(locRef, options);
			Map<String, TimeSeriesIds> tsIdsBySubMap = initTsIdsBySubLocation(outletsBySubMap.values(), association);
			LocationGroupSet lgs = getLocationGroupSet(locRef);
			if(lgs != null)
			{
				for(Map.Entry<String, IOutlet> entry : outletsBySubMap.entrySet())
				{
					String key = entry.getKey();
					IOutlet value = entry.getValue();
					LocationGroupRef locationGroupRef = value.getRatingGroupRef();

					LocationGroup locationGroup = lgs.getLocationGroup(locationGroupRef);
					List<String> controlParameters = getControlParameters(locationGroup, locRef);

					TimeSeriesIds tsIds = tsIdsBySubMap.get(key);
					updateParameters(tsIds, controlParameters);
				}
			}
			createGateSettingsOutlet(gc, locRef, startDate, end, iControlledOutlet, tsIdsBySubMap, options);
		}
		else
		{
			LOGGER.log(Level.WARNING, "Gate settings not created. Outlet does not exist: {0}", outletId);
		}
		gc.saveData(options);
	}

	@Override
	public void createGateSettingsOutletFromTs(String officeId, String locationStr, Date startDate, Date end, String outletId, String tsId)
			throws Exception
	{
		Metrics metrics = RegiMetricsService.createMetrics(this.getClass().getSimpleName(), "createGateSettingsOutletFromTs");
		OptionalParams options = new OptionalParams(metrics);
		LocationTemplate locRef = new LocationTemplate(officeId, locationStr);
		HeadlessGateCache gc = getCache(locRef, startDate, end, options);
		String from = _simpleDateFormat.format(startDate);
		String to = _simpleDateFormat.format(end);
		LOGGER.log(Level.INFO, "Creating gate settings using time series for " +
						"Office: {0} Location: {1} Outlet: {2} from: {3} to: {4} using time series {5}",
				new Object[]{officeId, locationStr, outletId, from, to, tsId});
		IControlledOutlet iControlledOutlet = getIControlledOutlet(gc, outletId);
		if(iControlledOutlet != null)
		{
			createGateSettingsOutlet(gc, locRef, startDate, end, iControlledOutlet, tsId, options);
		}
		else
		{
			LOGGER.log(Level.WARNING, "Gate settings not created. Outlet does not exist: {0}", outletId);
		}

		gc.saveData(options);
	}

	public IControlledOutlet getIControlledOutlet(GateCache gc, String outletId) {
		IControlledOutlet retval = null;
		IControlledOutletGroupContainer ogc = gc.getOutletGroupContainer();
		if (ogc != null) {
			Map<String, IControlledOutlet> outletMap = ogc.getOutletMap();
			if (outletMap != null) {
				retval = outletMap.get(outletId);
			}
		}
		return retval;
	}

	@Override
	public void createGateSettingsGroup(String officeId, String locationStr, Date startDate, Date end, String groupId) throws Exception
	{
		Metrics metrics = RegiMetricsService.createMetrics(this.getClass().getSimpleName(), "createGateSettingsGroup");
		OptionalParams options = new OptionalParams(metrics);
		LocationTemplate locRef = new LocationTemplate(officeId, locationStr);
		HeadlessGateCache gc = getCache(locRef, startDate, end, options);

		IControlledOutletGroupContainer ogc = gc.getOutletGroupContainer();
		String from = _simpleDateFormat.format(startDate);
		String to = _simpleDateFormat.format(end);
		LOGGER.log(Level.INFO, "Creating gate settings for outlet group using time series associations for " +
						"Office: {0} Location: {1} Outlet Group: {2} from: {3} to: {4}",
				new Object[]{officeId, locationStr, groupId, from, to});
		if(ogc != null)
		{
			IControlledOutletGroup outletGroup = ogc.getOutletGroup(groupId);
			if(outletGroup != null)
			{
				createGateSettingsGroup(gc, locRef, startDate, end, outletGroup, options);
			}
			else
			{
				LOGGER.log(Level.WARNING, "Gate settings not created. Outlet Group does not exist: {0}", groupId);
			}
		}

		gc.saveData(options);
	}

	public HeadlessGateCache getCache(LocationTemplate locRef, final Date startDate, final Date endDate, OptionalParams options) throws DbConnectionException, DbIoException,
			CacheInitializationException {

		RegiDomain domain = getRegiDomain();
		AtProjectManager atProjectManager = domain.getAtProjectManager(getManagerId());
		AtProjectDescriptor projectDescriptor = atProjectManager.getProjectDescriptor(locRef, CacheUsage.NORMAL);

		// This seems like a really big hack.  Is this really needed?
		final CountDownLatch latch = new CountDownLatch(2);
		IThreadedBlockRetriever completionCallbackTarget = new AbstractThreadedBlockRetriever() {

			@Override
			public void asyncHeadCacheFetchCompleted() {
				LOGGER.info("asyncHeadCacheFetchCompleted");
				latch.countDown();
			}

			@Override
			public void asyncTailCacheFetchCompleted() {
				LOGGER.info("asyncTailCacheFetchCompleted");
				latch.countDown();
			}

		};

		Set<Date> modifiedDatesForCachedSettings = null;
		int MAXROWSTORETRIEVE = 35;

		ICurrentDayControl currentDayControl = new ICurrentDayControl() {

			@Override
			public void setDate(Date date, boolean fireEvents) {
				throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
			}

			@Override
			public Date getCurrentDate() {
				return startDate;
			}

			@Override
			public int getLookbackDays() {
				return 2;
			}

			@Override
			public int getLookForwardDays() {
				return 3;
			}
		};
		
		HeadlessGateCache gateCache = new HeadlessGateCache(startDate, endDate, getManagerId(),
				projectDescriptor, MAXROWSTORETRIEVE, currentDayControl,
				completionCallbackTarget, modifiedDatesForCachedSettings);

		//GateCache gateCache = new GateCache(getManagerId(), projectDescriptor, 35, completionCallbackTarget, modifiedDatesForCachedSettings);
//        gateCache.setDisplayUnitSystem(hec.data.Units.SI_ID);  // does this matter?
//        Map<RowcpsFutureDescriptor, Object> futureMap = new HashMap<>();
		// need to set startDate on the control?
		// startDate //
		ThreadIdProvider idprov = new DefaultThreadIdProvider();
		gateCache.initCache(idprov, options);

		LOGGER.info("Waiting for GateCache to initialize.");
		boolean completedWithoutTimeout = false;
		try {
			// This needs more thought.  Peter thinks db timesout at 10 minutes.
			// Needs to be a value higher than any user would be willing to wait.
			
			Integer seconds = Integer.getInteger(LATCH_SECONDS, 11*60); // This one goes to 11...
			completedWithoutTimeout = latch.await(seconds, TimeUnit.SECONDS);        					
		} catch (InterruptedException ex) {
			Thread.currentThread().interrupt();
			LOGGER.log(Level.SEVERE, "Unable to wait for countdown latch on gate cache initialization. process was interrupted", ex);
		}

		if (completedWithoutTimeout) {
			LOGGER.info("GateCache is initialized.");
		} else {
			// error
			gateCache = null;
			LOGGER.info("GateCache failed to initialize.");
		}

		return gateCache;
	}

	public ITimeSeriesDescription getFirstTimeSeriesDescription(LocationTemplate locRef) throws DbConnectionException, DbIoException,
			DataObjectException {
		ITimeSeriesDescription tsDescription = null;

		RegiDomain regi = getRegiDomain();
		ManagerId manId = getManagerId();

		AtProjectManager atProjectManager = regi.getAtProjectManager(managerId);

//		IProject locProject = atProjectManager.getIProject(locRef, CacheUsage.NORMAL);
//		final IAssociationProvider<ITimeSeriesAssociation> tsProvider = locProject.getTimeSeriesAssociationProvider();
//        final IAssociationCatalog<ITimeSeriesAssociation> global = tsProvider.getGlobalOutputAssociations();
//        final IAssociationCatalog<ITimeSeriesAssociation> override = tsProvider.getOverrideOutputAssociations();
		AtAssociationManager<ITimeSeriesAssociation> assMan = regi.getAtTimeSeriesAssociationManager(manId);

		/// IProject.TsUsageId.GATESETTINGS_GATE_OPENING
		String assType = ITimeSeriesAssociation.LOCATION_TIME_SERIES_ASSOCIATION;

		// String usageCat = "Regi_*_OUTPUT";
		// String usageCat = Regi_gate_OUTPUT
		// String usageCat = IProject.TsUsageId.GATESETTINGS_GATE_OPENING.getUsageCategoryId(RegiDomain.getAppRootId(), InputOutput.INPUT);
		String usageCat = TsUsageId.GATESETTINGS_GATE_OPENING.getUsageCategoryId(RegiDomain.getAppRootId(), InputOutput.OUTPUT);
		String usageMask = TsUsageId.GATESETTINGS_GATE_OPENING.usage;   // GateSettings_gate_opening

		// AtAssociationManager.retrieveAssociations builds something like usageCat.usageMask.locRef
		// our gate association is like:
		// 	Regi_gate_OUTPUT.GateSettings_gate_opening.WTYT2
		IAssociationCatalog<ITimeSeriesAssociation> catalog = assMan.retrieveAssociations(locRef, assType, usageCat, usageMask);

		List<ITimeSeriesAssociation> tsas = catalog.getList();

		if (tsas != null && !tsas.isEmpty()) {
			ITimeSeriesAssociation first = tsas.iterator().next();

			tsDescription = first.getTimeSeriesId();
		}

		return tsDescription;
	}

	public Set<Long> getTimeOfChanges(ITimeSeriesDescription timeSeriesId, Date startDate, Date end, OptionalParams options) throws
			DataSetException, HecMathException, DbException {
		Set<Long> timeOfChanges = null;
		if (timeSeriesId != null) {

			RegiDomain regi = getRegiDomain();
			AtTimeSeriesManager tsManager = regi.getAtTimeSeriesManager(getManagerId());

			DataSetTx dataSetTX = getDataSetTx(timeSeriesId, startDate, end, tsManager, options);

			if (dataSetTX != null) {
				timeOfChanges = findChanges(dataSetTX);

			}

		}
		return timeOfChanges;
	}

	public DataSetTx getDataSetTx(ITimeSeriesDescription timeSeriesId, Date startDate, Date end, AtTimeSeriesManager tsManager, OptionalParams options) throws
			DataSetTxIllegalArgumentException, DbException, DataSetException
	{
		DescriptionTx dTx = timeSeriesId.getLookup().lookup(DescriptionTx.class);

		return getDataSetTx(startDate, end, dTx, tsManager, options);
	}

	public DataSetTx getDataSetTx(Date startDate, Date end, DescriptionTx dTx, AtTimeSeriesManager tsManager, OptionalParams options) throws DbException,
			DataSetException, DataSetTxIllegalArgumentException {
		DataSetTx dstx;
		String timeSeriesId1 = dTx.getTimeSeriesId();
		Units units = dTx.getParameter().getUnits();
		//Units units = new Units();
		DataSetTxTemplate dataSetTxTemplate = new DataSetTxTemplate(dTx, startDate.getTime(), end.getTime(), units);
		dstx = tsManager.retrieveDataSetTx(dataSetTxTemplate, CacheUsage.NORMAL, options);
		return dstx;
	}

	public NavigableSet<Long> findChanges(DataSetTx dataSetTX) throws HecMathException {
		NavigableSet<Long> set = null;
		if (dataSetTX != null) {
			set = new TreeSet<>();
			TimeSeriesContainer tsc = dataSetTX.getTimeSeriesContainer();
			TimeSeriesMath tsm = new TimeSeriesMath(tsc);

			double[] values = dataSetTX.getValuesWithQualityFlagsApplied();  // do we want this?
			long[] times = dataSetTX.getTimes();

			double lastValid = HecMath.UNDEFINED;

			// add the times of the internal changes.
			for (int i = 0; i < values.length; i++) {
				if (tsm.isValid(i)) {
					if (lastValid != values[i]) {
						lastValid = values[i];
						set.add(times[i]);
					}
				}
			}

			// add the bookends
			set.add(times[0]);
			set.add(times[times.length - 1]);
		}

		return set;
	}

	public void createGateSettingsGroup(HeadlessGateCache gc, LocationTemplate locRef, Date startDate, Date end, IControlledOutletGroup outletGroup, OptionalParams options)
			throws DataSetException, DbException, HecMathException {
		List<IControlledOutlet> outlets = outletGroup.getOutlets();

		if (outlets != null && !outlets.isEmpty()) {
			ITimeSeriesAssociation association = getInputAssociation(locRef);
			Map<String, IOutlet> outletsBySubMap = getOutletsBySubMap(locRef, options);

			Map<String, TimeSeriesIds> tsIdsBySubMap = initTsIdsBySubLocation(outletsBySubMap.values(), association);

			LocationGroupSet lgs = getLocationGroupSet(locRef);
			if (lgs != null) {
				for (Map.Entry<String, IOutlet> entry : outletsBySubMap.entrySet()) {
					String key = entry.getKey();
					IOutlet value = entry.getValue();
					LocationGroupRef locationGroupRef = value.getRatingGroupRef();

					LocationGroup locationGroup = lgs.getLocationGroup(locationGroupRef);
					List<String> controlParameters = getControlParameters(locationGroup, locRef);

					TimeSeriesIds tsIds = tsIdsBySubMap.get(key);
					updateParameters(tsIds, controlParameters);
				}
			}

			for (IControlledOutlet controlledOutlet : outlets) {
				createGateSettingsOutlet(gc, locRef, startDate, end, controlledOutlet, tsIdsBySubMap, options);
			}
		}
	}

	public static void updateParameters(TimeSeriesIds tsIds, List<String> controlParameters) {
		if (tsIds != null && controlParameters != null && !controlParameters.isEmpty()) {
			String firstControlParam = controlParameters.get(0);
			String originalParameter = tsIds.getParameter(0);
			
			if (originalParameter.endsWith("<None>"))//Special case for gate opening settings with <None>
			{
				try
				{
					Parameter param = new Parameter(firstControlParam);
					firstControlParam = param.getBaseParameter();
				}
				catch (DataSetIllegalArgumentException ex)
				{
					LOGGER.log(Level.SEVERE, "Unable to parse parameter " + originalParameter, ex);
				}
			}

			tsIds.setParameter(0, firstControlParam);  // updates parameter from "Opening" to "Opening-Spillway_Gate"
		}
	}

	private LocationGroupSet getLocationGroupSet(LocationTemplate locRef) throws DbConnectionException, DbIoException {
		RegiDomain regiDomain1 = getRegiDomain();
		AtProjectManager atProjectManager = regiDomain1.getAtProjectManager(getManagerId());
		AtProjectDescriptor currentDescriptor = atProjectManager.getProjectDescriptor(locRef, CacheUsage.NORMAL);
		LocationTemplate projectLocationRef = currentDescriptor.getProjectLocationRef();
		AtRatingManager atRatingManager = regiDomain1.getAtRatingManager(getManagerId());
		LocationCategoryRef ratingGroupCatRef = atRatingManager.getCategoryRef();
		String officeId = projectLocationRef.getOfficeId();

		AtLocationGroupManager atLocationGroupManager = regiDomain1.getAtLocationGroupManager(getManagerId());
		LocationGroupSet ratingGroups = atLocationGroupManager.retrieveLocationGroups(ratingGroupCatRef, officeId,
				projectLocationRef, null,
				CacheUsage.NORMAL);
		return ratingGroups;
	}

	/**
	 * Based on the method in OutletPanel..
	 *
	 * @param ratingLocGroup
	 * @param template
	 *
	 * @return
	 */
	private List<String> getControlParameters(LocationGroup ratingLocGroup, LocationTemplate template)
	{

		List<String> retval = new ArrayList<>();
		if (ratingLocGroup != null)
		{
			for (AssignedLocation assignedLocation : ratingLocGroup.getAssignedLocations())
			{
				if (assignedLocation.getAssociatedLocRef() != null && assignedLocation.getAssociatedLocRef().equals(template))
				{
					retval.add(assignedLocation.getAliasId());
				}
			}

			if (retval.isEmpty())
			{
				try
				{

					Parameter controlParameter = GateSettingsUtil.getGateOpeningParameter(ratingLocGroup);
					if (controlParameter != null)
					{
						retval.add(controlParameter.toString());
					}
				}
				catch (DataSetException ex)
				{
					LOGGER.log(Level.INFO, "unable to get control parameter for rating group {0}", ratingLocGroup.getDisplayName());
				}
			}
		}

		return retval;
	}

	public NavigableSet<Date> getDatesSubset(GateCache gc, Date start, Date end) {
		NavigableSet<Date> retval = new TreeSet<>();

		if (gc != null) {
			Date[] gateSettingKeys = gc.getGateSettingKeys();
			if (gateSettingKeys != null && gateSettingKeys.length > 0) {
				retval.addAll(Arrays.asList(gateSettingKeys));
				retval = retval.subSet(start, true, end, true);
			}
		}

		return retval;
	}

	private void createGateSettingsOutlet(HeadlessGateCache gc, LocationTemplate locRef, Date startDate, Date end,
			IControlledOutlet iControlledOutlet, Map<String, TimeSeriesIds> tsIdsBySubMap, OptionalParams options) throws DbConnectionException, DbIoException,
			DataSetIllegalArgumentException, DbException,
			DataSetException, HecMathException {
		if (iControlledOutlet != null) {

//				//	ITimeSeriesDescription timeSeriesId = association.getTimeSeriesId();
//		List<IOutlet> outlets = getIOutlets(regi, locProject);
//
//		Map<String, IOutlet> outletsBySubMap = new HashMap<>();
//		for (IOutlet outlet : outlets) {
//			outletsBySubMap.put(outlet.getLocation().getSubLocationId(), outlet);
//		}
//			String outletName = iControlledOutlet.getOutletName();   // this is like TG1 , not like WTYT2-TG1
			LOGGER.log(Level.FINE, "Getting first TS Description {0} {1}", new Object[]{
				locRef.toString(), iControlledOutlet.toString()
			});
			String tsIdStr = getFirstTimeSeriesDescription(locRef, iControlledOutlet.toString(), tsIdsBySubMap);
			createGateSettingsOutlet(gc, locRef, startDate, end, iControlledOutlet, tsIdStr, options);
		}
	}

	public void createGateSettingsOutlet(HeadlessGateCache gc, LocationTemplate locRef, Date startDate, Date end,
										 IControlledOutlet iControlledOutlet, String tsIdStr, OptionalParams options)
			throws DataSetException, DbException, HecMathException
	{
		AtTimeSeriesManager tsManager = getRegiDomain().getAtTimeSeriesManager(getManagerId());

		LOGGER.log(Level.INFO, "Comparing Gate settings at:{0} to timeseries:{1}", new Object[]
				{
						iControlledOutlet.getOutletName(), tsIdStr
				});

		if(tsIdStr != null)
		{
			DescriptionTx dtx = new DescriptionTx(locRef.getOfficeId(), tsIdStr);
			DataSetTx dataSetTx = getDataSetTx(dtx, startDate, end, tsManager, options);

			LOGGER.log(Level.INFO, "finding changes");
			NavigableSet<Long> changeTimes = findChanges(dataSetTx);
			if(changeTimes != null && !changeTimes.isEmpty())
			{

				NavigableSet<Date> closedDates = new TreeSet<>();
				NavigableMap<Date, Double> tsMap = dataSetTx.getDateValueNavigableMap();
				NavigableMap<Date, GateOpeningEntry> cacheEntries = findEntriesForOutlet(iControlledOutlet, gc, startDate, end, closedDates);
				// What if dateEntryMap is null or empty?
				//
				TreeSet<Date> datesOfModifications = new TreeSet<>();
				// Coming from the back lets us ignore the gate-entries we are adding.
				// Also we only care about the changes in the timeseries.
				for(Long changeTime : changeTimes)
				{
					if(changeTime != null)
					{
						Date tsDate = new Date(changeTime);
						Double tsValue = tsMap.get(tsDate);

						boolean hasDiff = hasDifferenceAtDate(gc, cacheEntries, tsValue, tsDate, closedDates);

						if(hasDiff)
						{
							Map.Entry<Date, GateOpeningEntry> floorEntry = getValidFloorEntry(cacheEntries, tsDate);
							// difference detected
							// immediately make the change and apply it

							GateSettingsBlock gateSettingBlock = gc.getGateSetting(tsDate);
							if(gateSettingBlock == null)
							{
								LOGGER.log(Level.INFO, "buildGateSettingsBlock");
								Date cacheFloorDate = closedDates.floor(tsDate);
								if(floorEntry != null)
								{
									Date floorEntryDate = floorEntry.getKey();
									if(cacheFloorDate == null || floorEntryDate.after(cacheFloorDate))
									{
										cacheFloorDate = floorEntryDate;
									}
								}

								gateSettingBlock = buildGateSettingsBlock(gc, cacheFloorDate, tsDate);

								gateSettingBlock.setModified(true);

								String dischargeCode = DischargeComputationRecord.DischargeComputationCode.EstimatedByUser.dbEquivalent();
								gateSettingBlock.setDischargeComputationCode(dischargeCode);
								gateSettingBlock.setReleaseReasonCode("O");
								gateSettingBlock.setChangeNotes("Regi Headless ");

								gc.putGateSetting(tsDate, gateSettingBlock);
							}

							try
							{
								gc.modifyGateOpeningBlock(tsDate, iControlledOutlet, tsValue);
								datesOfModifications.add(tsDate);
							}
							catch(GateMergeException ex)
							{
								LOGGER.log(Level.WARNING, "Error merging gate changes for date: "
										+ _simpleDateFormat.format(tsDate) + " value: " + tsValue, ex);
							}
						}

					}
				}

				String message = getMessage(datesOfModifications, iControlledOutlet.getOutletName());
				LOGGER.log(Level.INFO, message);
			}
			else
			{
				LOGGER.log(Level.INFO, "no changes found");
			}
		}
	}

	public static String getMessage(TreeSet<Date> datesOfModifications, String outletName) {
		ChoiceFormat beginningFormat = new ChoiceFormat(
				new double[]{
					0, 1, 2
				},
				new String[]{
					"No modifications were", "One modifcation was", "{2} modifications were"
				});

		ChoiceFormat endFormat = new ChoiceFormat(
				new double[]{
					0, 1, 2, 50
				},
				new String[]{
					".",
					" for the following date:{3}.",
					" for the following dates:{3}.",
					" for dates in the range {4} - {5}."
				});

		SimpleDateFormat sdf = new SimpleDateFormat("ddMMMyy HHmmss");

		MessageFormat mf = new MessageFormat("");
		mf.applyPattern("{0} made to the gate settings at {1}{2}");
		Format[] formats
				= {
					beginningFormat, null, endFormat, NumberFormat.getInstance(), sdf, sdf
				};
		mf.setFormats(formats);
		final Date first = datesOfModifications.isEmpty() ? null : datesOfModifications.first();
		final Date last = datesOfModifications.isEmpty() ? null : datesOfModifications.last();
		Object[] args
				= {
					datesOfModifications.size(), //{0}
					outletName, //{1}
					datesOfModifications.size(), //{2}
					datesOfModifications, //{3}
					first, //{4}
					last
				}; //{5}
		final String message = mf.format(args);
		return message;
	}

	public GateSettingsBlock buildGateSettingsBlock(GateCache gc, Date prevGateSettingDate, Date newDate) {
		ArrayList<AggregateGateOpeningEntry> goeList = new ArrayList<>();
		GateSettingsBlock prevGateSetting = null;
		GateSettingsBlock gsb = null;
		if (prevGateSettingDate != null) {
			prevGateSetting = gc.getGateSetting(prevGateSettingDate);
			if (prevGateSetting != null && prevGateSetting.getAggregateOpeningsSize() > 0) {
				for (int i = 0; i < prevGateSetting.getAggregateOpeningsSize(); i++) {
					IControlledOutletGroup outletGroup = prevGateSetting.getAggregateOpeningsElement(i).getOutletGroup();
					goeList.add(new AggregateGateOpeningEntry(outletGroup));
				}
			}
		}

		if (prevGateSetting == null) {
			// goeList should be full before the ctor call b/c GateSettingBlock adds listeners to the items in the goeList.
			gsb = new GateSettingsBlock(gc.getOutletGroupContainer().getOutletGroups(), goeList);
			boolean getActiveOnly = true;
			DischargeComputationCode disCode = DischargeComputationRecord.DischargeComputationCode.CalculatedFromRatingCurve;
			gsb.setDischargeComputationCode(disCode.dbEquivalent());
			final LookupRecordBase reasonCode = gc.getReleaseReasonCodes(getActiveOnly).get(0);
			gsb.setReleaseReasonCode(reasonCode.getShortDescription());
		} else {
			try {
				gsb = prevGateSetting.clone();
				gsb.setDischargeComputationCode(prevGateSetting.getDischargeComputationCode());
				gsb.setReleaseReasonCode(prevGateSetting.getReleaseReasonCode());
			} catch (CloneNotSupportedException ex) {
				LOGGER.log(Level.SEVERE, "Unable to clone previous gate setting, Clone operating not supported by class: "
						+ prevGateSetting.getClass().getName(), ex);
			}
		}

		Date rowDate = newDate;
		Date dateKey = newDate;
		HashMap<TimeSeriesDataContainer.TimeSeriesDataType, ConcurrentNavigableMap<Date, TimeSeriesDataContainer>> tsData = gc.getTimeSeriesDataForGateSettingsDateRange();

		if (tsData.isEmpty()) {
			LOGGER.fine("ts data is empty");
			// this is based what BulkSettingsModel does.
			ThreadIdProvider idprov = new DefaultThreadIdProvider();
		
			gc.extendTimeSeriesData(new Date(newDate.getTime() - 86400 * 1000), new Date(newDate.getTime() + 86400 * 1000), new OptionalParams(), idprov);
			// tsData = gc.getTimeSeriesDataForGateSettingsDateRange();  //shouldnt have to do this b/c extend should merge into tsData...
		}

		FineTuneRowElementSynthetic ftre = new FineTuneRowElementSynthetic(FineTuningRowType.GateChange, rowDate, dateKey, tsData, true);

		// based on BulkSettingsModel
		double poolElev = ftre.getPoolElevation();
		double tailElev = ftre.getTailwaterElevation();
		double refElev = ftre.getReferenceElevation();

		if (Double.isNaN(poolElev)) {
			poolElev = 0;
		}
		if (Double.isNaN(tailElev)) {
			tailElev = 0;
		}
		if (Double.isNaN(refElev)) {
			refElev = 0;
		}

		if(gsb != null)
		{
			gsb.setElevationCommon(poolElev);
			gsb.setIsElevationOverridden(false);
			gsb.setTailwaterCommon(tailElev);
			gsb.setIsTailwaterOveridden(false);
			gsb.setReferenceCommon(refElev);
			gsb.setIsReferenceOveridden(false);
			gsb.setModified(true);
		}

		return gsb;
	}

	public Map.Entry<Date, GateOpeningEntry> getValidFloorEntry(NavigableMap<Date, GateOpeningEntry> dateEntryMap, Date tsDate) {
		Map.Entry<Date, GateOpeningEntry> floorEntry = null;

		if (dateEntryMap != null) {
			Double value = null;
			Date nextKey = tsDate;
			while (nextKey != null && (value == null || !RMAConst.isValidValue(value))) {
				floorEntry = dateEntryMap.floorEntry(nextKey);
				value = getValueFromEntry(floorEntry);
				nextKey = dateEntryMap.lowerKey(nextKey);
			}
		}
		return floorEntry;
	}

	public Double getValueFromEntry(Map.Entry<Date, GateOpeningEntry> floorEntry) {
		Double retval = null;
		if (floorEntry != null) {
			GateOpeningEntry entry = floorEntry.getValue();
			// Date entryDate = floorEntry.getKey();
			AggregateGateOpeningEntry agoeHolding = entry.getParent();
			if (agoeHolding != null) {
				retval = agoeHolding.getGateOpeningCommon();
			}
		}
		return retval;
	}

	public NavigableMap<Date, GateOpeningEntry> findEntriesForOutlet(IControlledOutlet iControlledOutlet,
																	 GateCache gc, Date startDate, Date end,
																	 Set<Date> closedDates)
	{
		NavigableMap<Date, GateOpeningEntry> dateEntryMap = null;
		if (iControlledOutlet != null) {
			Date[] gateSettingKeys = gc.getGateSettingKeys();

			TreeSet<Date> dateset = new TreeSet<>();
			if (gateSettingKeys != null)
			{
				dateset.addAll(Arrays.asList(gateSettingKeys));
			}

			Date startAt = dateset.floor(startDate);
			// I think I need the date before the startDate too so that I know what it changed from at startDate?
			if (startAt == null)
			{
				startAt = startDate;
			}

			SortedSet<Date> subSet = dateset.subSet(startAt, true, end, true);

			// this is the way its structured in the cache
			NavigableMap<Date, Map<IControlledOutletGroup, Map<IControlledOutlet, GateOpeningEntry>>> dateGrpOutletEntryMap
					= buildDateGrpOutletEntryMap(subSet, gc);

			// Pretty sure it works better for me if it looks like this
			Map<IControlledOutletGroup, Map<IControlledOutlet, NavigableMap<Date, GateOpeningEntry>>> grpOutletDateMap
					= reorganize(dateGrpOutletEntryMap);

			IControlledOutletGroup group = iControlledOutlet.getParent();
			Map<IControlledOutlet, NavigableMap<Date, GateOpeningEntry>> outletDateEntryMap = null;
			if (grpOutletDateMap != null) {
				outletDateEntryMap = grpOutletDateMap.get(group);
			}
			if (outletDateEntryMap != null) {
				dateEntryMap = outletDateEntryMap.getOrDefault(iControlledOutlet, new TreeMap<>());
				
				for (Date date : subSet)
				{
					if (!dateEntryMap.containsKey(date))
					{
						closedDates.add(date);
					}
				}
			}
			
		}
		return dateEntryMap;
	}

	public NavigableMap<Date, Map<IControlledOutletGroup, Map<IControlledOutlet, GateOpeningEntry>>> buildDateGrpOutletEntryMap(
			SortedSet<Date> subSet, GateCache gc) {
		NavigableMap<Date, Map<IControlledOutletGroup, Map<IControlledOutlet, GateOpeningEntry>>> dateGrpOutletEntryMap = new TreeMap<>();
		if (subSet != null && !subSet.isEmpty()) {
			for (Date date : subSet) {
				GateSettingsBlock gsb = gc.getGateSetting(date);

				if (gsb != null) {
					List<AggregateGateOpeningEntry> entryList = gsb.getReadOnlyAggregateOpenings();
					if (entryList != null && !entryList.isEmpty()) {
						Map<IControlledOutletGroup, Map<IControlledOutlet, GateOpeningEntry>> map = new HashMap<>();
						dateGrpOutletEntryMap.put(date, map);
						for (AggregateGateOpeningEntry entry : entryList) {
							if (entry != null) {
								List<GateOpeningEntry> gateSettings = entry.getReadOnlyGateSettings();

								if (gateSettings != null && !gateSettings.isEmpty()) {
									IControlledOutletGroup controlledOutletGroup = entry.getOutletGroup();
									Map<IControlledOutlet, GateOpeningEntry> entries = map.get(controlledOutletGroup);
									
									if (entries == null) {
										entries = new HashMap<>();
										map.put(controlledOutletGroup, entries);
									}

									for (GateOpeningEntry setting : gateSettings) {
										if (setting != null) {
											entries.put(setting.getOutlet(), setting);
										}
									}
								}
							}
						}
					}
				}
			}
		}
		return dateGrpOutletEntryMap;
	}

	private Map<IControlledOutletGroup, Map<IControlledOutlet, NavigableMap<Date, GateOpeningEntry>>> reorganize(
			NavigableMap<Date, Map<IControlledOutletGroup, Map<IControlledOutlet, GateOpeningEntry>>> dateGrpOutletEntryMap) {
		Map<IControlledOutletGroup, Map<IControlledOutlet, NavigableMap<Date, GateOpeningEntry>>> retval = null;

		if (dateGrpOutletEntryMap != null) {
			retval = new HashMap<>();

			for (Map.Entry<Date, Map<IControlledOutletGroup, Map<IControlledOutlet, GateOpeningEntry>>> entry : dateGrpOutletEntryMap.
					entrySet()) {
				Date key = entry.getKey();
				Map<IControlledOutletGroup, Map<IControlledOutlet, GateOpeningEntry>> grpOutletEntryMap = entry.getValue();
				if (grpOutletEntryMap != null && !grpOutletEntryMap.isEmpty()) {
					for (Map.Entry<IControlledOutletGroup, Map<IControlledOutlet, GateOpeningEntry>> entry1 : grpOutletEntryMap.entrySet()) {
						IControlledOutletGroup outletGrp = entry1.getKey();
						Map<IControlledOutlet, GateOpeningEntry> outletEntryMap = entry1.getValue();

						if (outletEntryMap != null && !outletEntryMap.isEmpty()) {
							Map<IControlledOutlet, NavigableMap<Date, GateOpeningEntry>> retOutletDateEntryMap = retval.get(outletGrp);
							if (retOutletDateEntryMap == null) {
								retOutletDateEntryMap = new HashMap<>();
								retval.put(outletGrp, retOutletDateEntryMap);
							}

							for (Map.Entry<IControlledOutlet, GateOpeningEntry> entry2 : outletEntryMap.entrySet()) {
								IControlledOutlet outlet = entry2.getKey();
								GateOpeningEntry openningEntry = entry2.getValue();

								if (openningEntry != null) {

									NavigableMap<Date, GateOpeningEntry> retDateMap = retOutletDateEntryMap.get(outlet);
									if (retDateMap == null) {
										retDateMap = new TreeMap<>();
										retOutletDateEntryMap.put(outlet, retDateMap);
									}

									retDateMap.put(key, openningEntry);
								}
							}
						}
					}
				}
			}
		}

		return retval;

	}

	// not efficient for multiple outlets.  used by test.
	public String getFirstTimeSeriesDescription(LocationTemplate locRef, String outletId, OptionalParams options) throws DbConnectionException, DbIoException {
		ITimeSeriesAssociation association = getInputAssociation(locRef);
		Map<String, IOutlet> outletsBySubMap = getOutletsBySubMap(locRef, options);
		Map<String, TimeSeriesIds> tsIdsBySubMap = initTsIdsBySubLocation(outletsBySubMap.values(), association);
		return getFirstTimeSeriesDescription(locRef, outletId, tsIdsBySubMap);
	}

// outletId is like TG1
	public String getFirstTimeSeriesDescription(LocationTemplate locRef, String outletId, Map<String, TimeSeriesIds> tsIds) throws
			DbConnectionException, DbIoException {
		String retval = null;
		ITimeSeriesDescription tsDescription = null;

		if (tsIds != null) {
			TimeSeriesIds tsIdsForOutlet = tsIds.get(outletId);  // outletId is like TG1
			if (tsIdsForOutlet != null) {
				retval = tsIdsForOutlet.getId(0);
			}
		}
		return retval;
	}

	public ITimeSeriesAssociation getInputAssociation(LocationTemplate locRef) throws DbIoException, DbConnectionException {
		RegiDomain regi = getRegiDomain();
		ManagerId manId = getManagerId();

		AtProjectManager atProjectManager = regi.getAtProjectManager(manId);

		IProject locProject = atProjectManager.getIProject(locRef, CacheUsage.NORMAL);
		AtAssociationCache atAssociationCache = regi.getAtAssociationCache(manId);
		final IAssociationProvider<ITimeSeriesAssociation> tsProvider = atAssociationCache.getTimeSeriesAssociationsProvider(locProject.getLocation().getLocationTemplate());
		ITimeSeriesAssociation association = tsProvider.getInputAssociation(TsUsageId.GATESETTINGS_GATE_OPENING.usage);
		return association;
	}

	private Map<String, IOutlet> getOutletsBySubMap(LocationTemplate locRef, OptionalParams options) throws DbConnectionException, DbIoException {
		Map<String, IOutlet> outletsBySubMap = new HashMap<>();
		RegiDomain regi = getRegiDomain();
		ManagerId manId = getManagerId();

		AtProjectManager atProjectManager = regi.getAtProjectManager(manId);

		IProject locProject = atProjectManager.getIProject(locRef, CacheUsage.NORMAL);

		//	ITimeSeriesDescription timeSeriesId = association.getTimeSeriesId();
		List<IOutlet> outlets = getIOutlets(regi, locProject, options);
		for (IOutlet outlet : outlets) {
			if (outlet != null) {
				Location location = outlet.getLocation();
				if (location != null) {
					outletsBySubMap.put(location.getSubLocationId(), outlet);
				}
			}
		}
		return outletsBySubMap;
	}

	public List<IOutlet> getIOutlets(RegiDomain regi, IProject locProject, OptionalParams options) throws DbConnectionException, DbIoException {
		AtOutletManager atOutletManager = regi.getAtOutletManager(managerId);
		List<IOutlet> outlets = new ArrayList<>();
		List<IPhysicalStructure> physicalStructures = atOutletManager.retrieveList(locProject.getLocation().getLocationTemplate(),
				CacheUsage.NORMAL, options);
		for (IPhysicalStructure physicalStructure : physicalStructures) {
			if (physicalStructure instanceof IOutlet) {
				outlets.add((IOutlet) physicalStructure);
			}

		}
		return outlets;
	}

	private Map<String, TimeSeriesIds> initTsIdsBySubLocation(Collection<IOutlet> outlets, ITimeSeriesAssociation association) {
		Map<String, TimeSeriesIds> retval = new HashMap<>();

		if (association != null && association.getTimeSeriesId() != null) {
			//sub in the time series id for each outlet
			ITimeSeriesDescription tsId = association.getTimeSeriesId();

			for (IOutlet outlet : outlets) {
				String str = outlet.toString();  // like WTYT2-TG1
				String subLocationId = outlet.getLocation().getSubLocationId();  // like TG1
				TimeSeriesIds tsIds = new TimeSeriesIds();
				tsIds.add(tsId.getTimeSeriesId(), association.getOffsetSec());
				tsIds.setLocation(str);
				retval.put(subLocationId, tsIds);
			}

		} else {
			String type = ParameterType.getAvailableParameterTypes()[0];
			String interval = Interval.getAvailableIntervals()[0];
			String duration = Duration.getAvailableDurations()[0];
			String version = "MANUAL";
			int offset = UtcOffsetConst.NO_UTC_OFFSET;

			for (IOutlet outlet : outlets) {
				String subLocationId = outlet.getLocation().getSubLocationId();  // like TG1
				String str = outlet.toString();
				TimeSeriesIds tsIds = new TimeSeriesIds();
				tsIds.setLocation(str);
				tsIds.add("", type, interval, duration, version, offset);

				retval.put(subLocationId, tsIds);

			}
		}

		return retval;
	}
	
	private boolean isEntryAfterNearestClosedDate(NavigableSet<Date> closedDates, Map.Entry<Date, GateOpeningEntry> floorEntry, Date tsDate)
	{
		boolean output = true;
		Date nearestClose = closedDates.floor(tsDate);
		
		if (floorEntry != null && nearestClose != null)
		{
			Date key = floorEntry.getKey();
			output = key.after(nearestClose);
		}
		
		return output;
	}

	private boolean hasDifferenceAtDate(HeadlessGateCache cache, NavigableMap<Date, GateOpeningEntry> dateEntryMap, Double tsValue, Date tsDate, NavigableSet<Date> closedDates)
	{
		boolean output = true;
		
		if (dateEntryMap != null && tsValue != null && RMAConst.isValidValue(tsValue))
		{
			Map.Entry<Date, GateOpeningEntry> floorEntry = getValidFloorEntry(dateEntryMap, tsDate);
			boolean afterNearestClose = isEntryAfterNearestClosedDate(closedDates, floorEntry, tsDate);
			
			if (floorEntry != null && afterNearestClose)
			{
				Double cacheValueInEffectAtDate = getValueFromEntry(floorEntry);
				
				if (Objects.equals(cacheValueInEffectAtDate, tsValue))
				{
					output = false;
				}
			}
			//Floor entry is null, or there's a closed entry before this date.
			//If it's closed, and there's a null or closed value before it, then we haven't changed.
			else if (cache.isClosedGateOpening(tsValue))
			{
				output = false;
			}
		}

		return output;
	}

}

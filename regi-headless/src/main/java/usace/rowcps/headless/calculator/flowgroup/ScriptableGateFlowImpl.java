package usace.rowcps.headless.calculator.flowgroup;

import hec.data.location.LocationTemplate;
import hec.data.project.AtProjectDescriptor;
import hec.data.project.IProject;
import hec.db.DbConnectionException;
import hec.db.DbIoException;
import java.time.Instant;
import java.util.Calendar;
import java.util.Date;
import java.util.Map;
import java.util.TimeZone;
import java.util.logging.Level;
import java.util.logging.Logger;
import usace.metrics.services.Metrics;
import usace.rowcps.computation.ITimeSeriesComputationResult;
import usace.rowcps.computation.TimeSeriesComputationError;
import usace.rowcps.data.flowgroup.FlowGroupTimeSeries;
import usace.rowcps.data.flowgroup.IFlowGroup;
import usace.rowcps.headless.calculator.AbstractScriptableCalc;
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
public class ScriptableGateFlowImpl extends AbstractScriptableCalc implements ScriptableGateFlowCalc, ScriptableCalc {

	private static final Logger logger = Logger.getLogger(ScriptableGateFlowImpl.class.getName());

	public ScriptableGateFlowImpl(RegiDomain regiDomain, ManagerId manId) {
		super(regiDomain, manId);
	}

	@Override
	public void computeAll(String officeId, String locationId, Date start, Date end) {

		computeAll(officeId, locationId, start.getTime(), end.getTime());

	}

	@Override
	public void computeAll(String officeId, String locationId, Instant start, Instant end) {

		computeAll(officeId, locationId, start.toEpochMilli(), end.toEpochMilli());

	}

	@Override
	public void computeAll(String officeId, String locationId, long startTime, long endTime) {
            
            try
            {
                Metrics metrics = RegiMetricsService.createMetrics(this.getClass().getSimpleName(), "computeAll");
                OptionalParams options = new OptionalParams(metrics);
                
                AtProjectDescriptor projDesc = new AtProjectDescriptor();
                projDesc.setProjectLocationRef(new LocationTemplate(officeId, locationId));
                
                RegiDomain currentProject = (RegiDomain) RegiDomain.getCurrentProject();
        
                LocationTemplate projectLocationRef = projDesc.getProjectLocationRef();

                AtProjectManager atProjectManager = currentProject.getAtProjectManager(getManagerId());
                IProject iProject = atProjectManager.getIProject(projectLocationRef, CacheUsage.NORMAL);
                TimeZone timeZone = iProject.getProjectTimeZone();
                
                possiblyWarnAboutMilliseconds(startTime, endTime);
                
                HeadlessDbCommitFlowGroupCalc calc = new HeadlessDbCommitFlowGroupCalc(projDesc);
                calc.calcTimeSeries(getManagerId(),
                        projDesc.getProjectLocationRef(),
                        null,
                        null,
                        new Date(startTime),
                        new Date(endTime),
                        CacheUsage.NORMAL,
                        options,
                        timeZone);
            } catch (DbIoException | DbConnectionException ex)
            {
                logger.log(Level.SEVERE, null, ex);
            }
	}

	@Override
	public void computeAll(String officeId, String[] locationIds, Date start, Date end) {
		for (String locationId : locationIds) {
			computeAll(officeId, locationId, start, end);
		}
	}

	@Override
	public void computeAll(String officeId, String[] locationIds, Instant start, Instant end) {
		for (String locationId : locationIds) {
			computeAll(officeId, locationId, start, end);
		}
	}

	@Override
	public void computeAll(String officeId, String[] locationIds, long startTime, long endTime) {
		for (String locationId : locationIds) {
			computeAll(officeId, locationId, startTime, endTime);
		}
	}

	@Override
	public void computeFlowGroup(String officeId, String locationId, Date start, Date end, String groupId) {
		long startTime = start.getTime();
		long endTime = end.getTime();
		computeFlowGroup(officeId, locationId, startTime, endTime, groupId);
	}

	@Override
	public void computeFlowGroup(String officeId, String locationId, Instant start, Instant end, String groupId) {
		computeFlowGroup(officeId, locationId, start.toEpochMilli(), end.toEpochMilli(), groupId);
	}

	@Override
	public void computeFlowGroup(String officeId, String locationId, long startTime, long endTime, String groupId) {
		
            try
            {
                Metrics metrics = RegiMetricsService.createMetrics(this.getClass().getSimpleName(), "computeAll");
                OptionalParams options = new OptionalParams(metrics);
                
                AtProjectDescriptor projDesc = new AtProjectDescriptor();
                projDesc.setProjectLocationRef(new LocationTemplate(officeId, locationId));
                
                RegiDomain currentProject = (RegiDomain) RegiDomain.getCurrentProject();
        
                LocationTemplate projectLocationRef = projDesc.getProjectLocationRef();

                AtProjectManager atProjectManager = currentProject.getAtProjectManager(getManagerId());
                IProject iProject = atProjectManager.getIProject(projectLocationRef, CacheUsage.NORMAL);
                TimeZone timeZone = iProject.getProjectTimeZone();
                
                possiblyWarnAboutMilliseconds(startTime, endTime);
                
                HeadlessDbCommitFlowGroupCalc calc = new HeadlessDbCommitFlowGroupCalc(projDesc);
                calc.calcTimeSeries(getManagerId(),
                        projDesc.getProjectLocationRef(),
                        null,
                        groupId,
                        new Date(startTime),
                        new Date(endTime),
                        CacheUsage.NORMAL,
                        options,
                        timeZone);
                
            } catch (DbIoException | DbConnectionException ex)
            {
                logger.log(Level.SEVERE, "Unable to compute flow group " + groupId + " for " + locationId, ex);
            }
            
	}

	@Override
	public void computeFlowGroup(String officeId, String[] locationIds, Date start, Date end, String groupId) {
		long startTime = start.getTime();
		long endTime = end.getTime();
		for (String locationId : locationIds) {
			computeFlowGroup(officeId, locationId, startTime, endTime, groupId);
		}
	}

	@Override
	public void computeFlowGroup(String officeId, String[] locationIds, Instant start, Instant end, String groupId) {
		long startTime = start.toEpochMilli();
		long endTime = end.toEpochMilli();
		for (String locationId : locationIds) {
			computeFlowGroup(officeId, locationId, startTime, endTime, groupId);
		}
	}

	@Override
	public void computeFlowGroup(String officeId, String[] locationIds, long startTime, long endTime, String groupId) {
		for (String locationId : locationIds) {
			computeFlowGroup(officeId, locationId, startTime, endTime, groupId);
		}
	}

	private void possiblyWarnAboutMilliseconds(long start, long end) {
		possiblyWarnAboutMilliseconds(new Date(start), new Date(end));
	}

	private void possiblyWarnAboutMilliseconds(Date startDate, Date endDate) {
		Calendar cal = Calendar.getInstance(TimeZone.getTimeZone("UTC"));
		cal.clear();
		cal.setTime(startDate);
		boolean startHasSecOrMillis = cal.get(Calendar.MILLISECOND) != 0 || cal.get(Calendar.SECOND) != 0;
		cal.clear();
		cal.setTime(endDate);
		boolean endHasSecOrMillis = cal.get(Calendar.MILLISECOND) != 0 || cal.get(Calendar.SECOND) != 0;

		String end = "Typically times are only specified to the hour or minute. "
				+ "Using seconds or milliseconds can cause errors because these times do not align with the expected intervals.  "
				+ "If these times have been generated by java.util.Calendar then calling clear() before setting individual "
				+ "fields will reset calendar values to 0.  Alternatively calendar.set(Calendar.MILLISECOND, 0) "
				+ "and calendar.set(Calendar.SECOND, 0) will clear millisecond and second values. ";

		String message = null;

		if (startHasSecOrMillis && endHasSecOrMillis) {
			message = "The supplied start and end times have non-zero seconds or milliseconds components. " + end;

		} else if (startHasSecOrMillis) {
			message = "The supplied start time has a non-zero second or millisecond component. " + end;

		} else if (endHasSecOrMillis) {
			message = "The supplied end time has a non-zero second or millisecond component. " + end;
		}

		if (message != null) {
			boolean onlyWarn = Boolean.getBoolean("rowcps.headless.warn_and_continue");
			if (onlyWarn) {
				logger.log(Level.WARNING, message);
			} else {
				throw new IllegalArgumentException(message);
			}
		}
	}

	private void logErrors(Map<FlowGroupTimeSeries, ITimeSeriesComputationResult> calcTimeSeries, IFlowGroup flowGroup) {
		if (calcTimeSeries != null) {
			for (FlowGroupTimeSeries fgts : calcTimeSeries.keySet()) {
				ITimeSeriesComputationResult result = calcTimeSeries.get(fgts);

				if (result instanceof TimeSeriesComputationError) {
					logger.log(Level.SEVERE, "{0} failed to compute due to:\n{1}", new Object[]{fgts.toString(), ((TimeSeriesComputationError) result).getMessage()});
					logger.log(Level.SEVERE, "Stacktrace:", (Exception) result);
				}
			}

			if (flowGroup.getOutputTimeSeriesList().isEmpty()) {
				logger.log(Level.SEVERE, "No output time series set on flow group.");
			}
		}
	}
}

package usace.rowcps.headless.calculator.gatesettings;

import java.time.Instant;
import java.util.Date;

/**
 *
 * @author ryan
 */
public interface ScriptableGateSettings
{
	/**
	 * @deprecated Use {@link #createGateSettings(String, String, Instant, Instant)} instead. java.util.Date
	 * requires callers to build a java.util.Calendar with an explicit TimeZone to avoid relying on the JVM's
	 * default timezone; Instant is an unambiguous point in time.
	 */
	@Deprecated
	void createGateSettings(String officeId, String locationStr, Date startDate, Date end) throws Exception;
	void createGateSettings(String officeId, String locationStr, Instant startDate, Instant end) throws Exception;

	/**
	 * @deprecated Use {@link #createGateSettingsGroup(String, String, Instant, Instant, String)} instead.
	 */
	@Deprecated
	void createGateSettingsGroup(String officeId, String locationStr, Date startDate, Date end, String groupId) throws Exception;
	void createGateSettingsGroup(String officeId, String locationStr, Instant startDate, Instant end, String groupId) throws Exception;

	/**
	 * @deprecated Use {@link #createGateSettingsOutlet(String, String, Instant, Instant, String)} instead.
	 */
	@Deprecated
	void createGateSettingsOutlet(String officeId, String locationStr, Date startDate, Date end, String outletId) throws Exception;
	void createGateSettingsOutlet(String officeId, String locationStr, Instant startDate, Instant end, String outletId) throws Exception;

	/**
	 * @deprecated Use {@link #createGateSettingsOutletFromTs(String, String, Instant, Instant, String, String)} instead.
	 */
	@Deprecated
	void createGateSettingsOutletFromTs(String officeId, String locationStr, Date startDate, Date end, String outletId, String tsId) throws Exception;
	void createGateSettingsOutletFromTs(String officeId, String locationStr, Instant startDate, Instant end, String outletId, String tsId) throws Exception;
}

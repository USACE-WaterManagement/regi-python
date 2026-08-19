package usace.rowcps.headless.calculator.flowgroup;

import java.time.Instant;
import java.util.Date;

/**
 *
 * @author ryan
 */
public interface ScriptableGateFlowCalc
{

	/**
	 * @deprecated Use {@link #computeAll(String, String, Instant, Instant)} instead. java.util.Date
	 * requires callers to build a java.util.Calendar with an explicit TimeZone to avoid relying on
	 * the JVM's default timezone; Instant is an unambiguous point in time.
	 */
	@Deprecated
	void computeAll(String officeId, String locationId, Date start, Date end);
	/**
	 * @deprecated Use {@link #computeAll(String, String, Instant, Instant)} instead. A bare epoch-millis
	 * long has no explicit unit/type safety in scripts; Instant is self-documenting.
	 */
	@Deprecated
	void computeAll(String officeId, String locationId, long startTime, long endTime);
	void computeAll(String officeId, String locationId, Instant start, Instant end);

	/**
	 * @deprecated Use {@link #computeAll(String, String[], Instant, Instant)} instead.
	 */
	@Deprecated
	void computeAll(String officeId, String[] locationIds, Date start, Date end);
	/**
	 * @deprecated Use {@link #computeAll(String, String[], Instant, Instant)} instead.
	 */
	@Deprecated
	void computeAll(String officeId, String[] locationIds, long startTime, long endTime);
	void computeAll(String officeId, String[] locationIds, Instant start, Instant end);

	/**
	 * @deprecated Use {@link #computeFlowGroup(String, String, Instant, Instant, String)} instead.
	 */
	@Deprecated
	void computeFlowGroup(String officeId, String locationId, Date start, Date end, String groupId);
	/**
	 * @deprecated Use {@link #computeFlowGroup(String, String, Instant, Instant, String)} instead.
	 */
	@Deprecated
	void computeFlowGroup(String officeId, String locationId, long startTime, long endTime, String groupId);
	void computeFlowGroup(String officeId, String locationId, Instant start, Instant end, String groupId);

	/**
	 * @deprecated Use {@link #computeFlowGroup(String, String[], Instant, Instant, String)} instead.
	 */
	@Deprecated
	void computeFlowGroup(String officeId, String[] locationIds, Date start, Date end, String groupId);
	/**
	 * @deprecated Use {@link #computeFlowGroup(String, String[], Instant, Instant, String)} instead.
	 */
	@Deprecated
	void computeFlowGroup(String officeId, String[] locationIds, long startTime, long endTime, String groupId);
	void computeFlowGroup(String officeId, String[] locationIds, Instant start, Instant end, String groupId);

}

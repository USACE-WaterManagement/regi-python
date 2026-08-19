package usace.rowcps.headless.calculator.inflow;

import java.time.Instant;
import java.util.Date;

/**
 *
 * @author ryan
 */
public interface ScriptableInflow
{

	/**
	 * @deprecated Use {@link #autoAdjust(String, String, Instant)} instead. java.util.Date
	 * requires callers to build a java.util.Calendar with an explicit TimeZone to avoid
	 * relying on the JVM's default timezone; Instant is an unambiguous point in time.
	 */
	@Deprecated
	void autoAdjust(String officeId, String locationStr, Date startDate);

	void autoAdjust(String officeId, String locationStr, Instant startDate);

	/**
	 * @deprecated Use {@link #autoAdjust(String, String, Instant, boolean, boolean)} instead.
	 */
	@Deprecated
	void autoAdjust(String officeId, String locationStr, Date startDate, boolean useLimits, boolean freezeRain);

	void autoAdjust(String officeId, String locationStr, Instant startDate, boolean useLimits, boolean freezeRain);

	/**
	 * @deprecated Use {@link #cloneInflows(String, String, Instant)} instead.
	 */
	@Deprecated
	void cloneInflows(String officeId, String locationStr, Date startDate);

	void cloneInflows(String officeId, String locationStr, Instant startDate);

	/**
	 * @deprecated Use {@link #zeroNegatives(String, String, Instant)} instead.
	 */
	@Deprecated
	void zeroNegatives(String officeId, String locationStr, Date startDate);

	void zeroNegatives(String officeId, String locationStr, Instant startDate);

	/**
	 * @deprecated Use {@link #balanceAll(String, String, Instant)} instead.
	 */
	@Deprecated
	void balanceAll(String officeId, String locationStr, Date startDate);

	void balanceAll(String officeId, String locationStr, Instant startDate);

	/**
	 * @deprecated Use {@link #computeInflow(String, String, Instant, Instant)} instead.
	 */
	@Deprecated
	void computeInflow(String officeId, String locationStr, Date startDate, Date endDate);

	void computeInflow(String officeId, String locationStr, Instant startDate, Instant endDate);

	/**
	 * @deprecated Use {@link #computeEvapAsFlow(String, String, Instant, Instant)} instead.
	 */
	@Deprecated
	void computeEvapAsFlow(String officeId, String locationStr, Date startDate, Date endDate);

	void computeEvapAsFlow(String officeId, String locationStr, Instant startDate, Instant endDate);

	void setComputationStorageOptions(InflowComputationStorageOption option, InflowComputationStorageOption... options);
}

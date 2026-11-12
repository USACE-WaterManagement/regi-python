package usace.rowcps.headless.calculator.inflow;

import org.openide.util.lookup.ServiceProvider;
import usace.rowcps.headless.ScriptableCalcFactory;
import usace.rowcps.headless.interfaces.ScriptableCalc;
import usace.rowcps.regi.model.ManagerId;
import usace.rowcps.regi.model.RegiDomain;

/**
 *
 * @author ryan
 */
@ServiceProvider(service = ScriptableCalcFactory.class)
public class InflowCalcFactory implements ScriptableCalcFactory
{

	@Override
	public String getName()
	{
		return "Inflow";
	}

	@Override
	public String getDescription()
	{
		return "Recalculates Inflow at a Location";
	}

	@Override
	public String getUsage()
	{
		return "";
	}

	@Override
	public ScriptableCalc build(RegiDomain regiDomain, ManagerId managerid)
	{
		return new ScriptableInflowImpl(regiDomain, managerid);
	}

}
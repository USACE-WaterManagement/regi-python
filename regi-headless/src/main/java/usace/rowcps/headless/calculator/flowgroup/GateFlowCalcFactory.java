package usace.rowcps.headless.calculator.flowgroup;

import org.openide.util.lookup.ServiceProvider;
import usace.rowcps.headless.interfaces.ScriptableCalc;
import usace.rowcps.headless.ScriptableCalcFactory;
import usace.rowcps.regi.model.ManagerId;
import usace.rowcps.regi.model.RegiDomain;



/**
 *
 * @author ryan
 */
@ServiceProvider(service = ScriptableCalcFactory.class)
public class GateFlowCalcFactory implements ScriptableCalcFactory
{

	@Override
	public String getName()
	{
		return "Gate Flow";
	}

	@Override
	public String getDescription()
	{
		return "Does stuff";
	}

	@Override
	public String getUsage()
	{
		return "You need to call it to use it...";
	}

	@Override
	public ScriptableCalc build(RegiDomain regiDomain, ManagerId managerid)
	{
		return new ScriptableGateFlowImpl(regiDomain, managerid);
	}

}

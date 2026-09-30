package usace.rowcps.headless.calculator.gatesettings;

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
public class GateSettingsCalcFactory implements ScriptableCalcFactory
{

	@Override
	public String getName()
	{
		return "Gate Settings";
	}

	@Override
	public String getDescription()
	{
		return "Adjusts Gate Settings";
	}

	@Override
	public String getUsage()
	{
		return "";
	}

	@Override
	public ScriptableCalc build(RegiDomain regiDomain, ManagerId managerid)
	{
		return new ScriptableGateSettingsImpl(regiDomain, managerid);
	}

}
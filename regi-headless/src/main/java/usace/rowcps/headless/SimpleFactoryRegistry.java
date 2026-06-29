package usace.rowcps.headless;

import usace.rowcps.headless.calculator.CalcFactoryRegistry;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.logging.Logger;
import rma.util.lookup.Lookup;

/**
 *
 * @author ryan
 */
public class SimpleFactoryRegistry extends CalcFactoryRegistry
{

	private static final Logger logger = Logger.getLogger(SimpleFactoryRegistry.class.getName());

	@Override
	public Collection<ScriptableCalcFactory> getFactories()
	{
		Collection<? extends ScriptableCalcFactory> lookupAll = Lookup.getDefault().lookupAll(
			ScriptableCalcFactory.class);
		if(lookupAll == null || lookupAll.isEmpty()){
			logger.warning("No ScriptableCalcFactory objects found in the lookup. "
					+ "There must have been a problem running the @Service annotation processor during the build.");
		}
		List<ScriptableCalcFactory> factories = new ArrayList<>();
		factories.addAll(lookupAll);
		return factories;
	}

	@Override
	public ScriptableCalcFactory getFactory(String name)
	{
		ScriptableCalcFactory retval = null;
		Collection<ScriptableCalcFactory> factories = getFactories();
		for (ScriptableCalcFactory factory : factories) {
			if (name.equals(factory.getName())) {
				retval = factory;
				break;
			}
		}

		return retval;
	}

	@Override
	public Collection<String> getNames()
	{
		List<String> names = new ArrayList<>();
		Collection<ScriptableCalcFactory> factories = getFactories();
		for (ScriptableCalcFactory factory : factories) {
			names.add(factory.getName());
		}

		return names;
	}
}

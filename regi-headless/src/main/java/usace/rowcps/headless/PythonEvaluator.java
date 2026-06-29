package usace.rowcps.headless;

import usace.rowcps.headless.interfaces.ScriptEvaluator;
import java.io.Reader;
import java.util.Map;
import javax.script.Bindings;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.ScriptException;
import javax.script.SimpleScriptContext;

/**
 *
 * @author ryan
 */
public class PythonEvaluator implements ScriptEvaluator
{

	public final static String ENGINE_NAME = "python";
	private static final String REFERENCE_ERROR = "ReferenceError";
	private static final String NAME_ERROR = "NameError";

	@Override
	public Object evaluateExpression(Reader reader, Map<String, Object> variables)
	{

		// I think this would let us restrict the classes loadable by python.
		ClassLoader ctxtLoader = Thread.currentThread().getContextClassLoader();

		ScriptEngineManager scriptManager = new ScriptEngineManager(ctxtLoader);
		ScriptEngine pythonEngine = scriptManager.getEngineByName(ENGINE_NAME);

		SimpleScriptContext context = (SimpleScriptContext) pythonEngine.getContext();

		Object javaValue = null;
		try {
			Bindings bindings = populateBingings(pythonEngine, variables); // fyi bindings actually SimpleBindings
			javaValue = pythonEngine.eval(reader, bindings);
		} catch (ScriptException e) {
			handleException(e, variables);
		}
		return javaValue;
	}

	private static Bindings populateBingings(ScriptEngine engine, Map<String, Object> variables)
	{
		Bindings bindings = engine.createBindings();
		for (Map.Entry<String, Object> entrySet : variables.entrySet()) {
			String name = entrySet.getKey();
			Object value = entrySet.getValue();
			bindings.put(name, value);
		}

		return bindings;
	}

	private static Object handleException(ScriptException exception, Map<String, Object> variables)
	{
		if (isReferenceError(exception)) {
			throw new IllegalArgumentException("Couldn't resolve some variables in expression with vars " + variables.
				keySet(), exception);
		}
		throw new RuntimeException(exception);
	}

	private static boolean isReferenceError(ScriptException exception)
	{
		String message = exception.getMessage();
		return message.startsWith(REFERENCE_ERROR);
	}

}

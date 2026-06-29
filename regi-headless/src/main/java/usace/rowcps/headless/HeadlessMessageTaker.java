package usace.rowcps.headless;

import com.rma.message.Message;
import com.rma.message.MessageTaker;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author ryan
 */
public class HeadlessMessageTaker implements MessageTaker
{
	private static final Logger logger = Logger.getLogger(HeadlessMessageTaker.class.getName());

	@Override
	public void addMessage(String string)
	{
		logger.log(Level.INFO, string);
	}

	@Override
	public void addMessage(Message msg)
	{
		logger.log(Level.INFO, msg.toString());
	}

	@Override
	public void addMessage(String string, String string1)
	{
		logger.log(Level.INFO, "{0} {1}", new String[]{string, string1});
	}

	@Override
	public void addMessage(String string, Message msg)
	{
		logger.log(Level.INFO, "{0} {1}", new String[]{string, msg.toString()});
	}

	@Override
	public void addMessage(String string, String string1, boolean showProgress)
	{
		logger.log(Level.INFO, "{0} {1}", new String[]{string, string1});
	}

	@Override
	public void addMessage(String string, Message msg, boolean showProgress)
	{
		logger.log(Level.INFO, "{0} {1}", new String[]{string, msg.toString()});
	}

}

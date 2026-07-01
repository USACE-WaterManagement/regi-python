/*
 * Copyright (c) 2018
 * United States Army Corps of Engineers - Hydrologic Engineering Center (USACE/HEC)
 * All Rights Reserved.  USACE PROPRIETARY/CONFIDENTIAL.
 * Source may not be released without written approval from HEC
 */
package usace.rowcps.headless;

import java.awt.GridLayout;
import java.awt.HeadlessException;
import java.awt.event.ActionEvent;
import java.io.IOException;
import java.nio.file.FileVisitOption;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.List;
import java.util.ArrayList;
import static java.util.stream.Collectors.toList;
import javax.swing.AbstractAction;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.SwingUtilities;

/**
 *
 * @author @author <a href="mailto:ryanm@rmanet.com">Ryan A. Miles (ryanm@rmanet.com)</a>
 */
public class TestFrame extends JFrame
{
	private static final Logger LOGGER = Logger.getLogger(TestFrame.class.getName());
	private final ExecutorService _executor = Executors.newSingleThreadExecutor();
	private final List<JButton> _buttons = new ArrayList<>();
	
	public TestFrame() throws HeadlessException
	{
		buildComponents();
	}

	public static void main(String[] args)
	{
		TestFrame frame = new TestFrame();
		frame.pack();
		frame.setDefaultCloseOperation(EXIT_ON_CLOSE);
		frame.setMinimumSize(frame.getPreferredSize());
		frame.setVisible(true);
	}

	private void buildComponents()
	{
		setLayout(new GridLayout(0, 3, 2, 2));
		
		String[] files = readFilesInTestFolder();

		for (String testData : files)
		{
			JButton btn = new JButton(new ButtonAction(testData, testData));
			_buttons.add(btn);
			add(btn);
		}
	}
	
	private String[] readFilesInTestFolder()
	{
		Path path = Paths.get(TestHeadless.getJythonTestFolder());
		List<String> paths = new ArrayList<>();
		try
		{
			paths.addAll(Files.walk(path, FileVisitOption.FOLLOW_LINKS)
					.map(Path::getFileName)
					.map(Path::toString)
					.filter(file -> file.endsWith("py"))
					.collect(toList()));
		}
		catch (IOException | RuntimeException ex)
		{

		}
		
		return paths.toArray(new String[0]);
	}
	
	private void performHeadless(String file)
	{
		disableButtons();
		
		_executor.submit(() -> 
		{
			String[] args = TestHeadless.getArgsForFile(file);
			try
			{
				RegiCLI.runHeadlessTest(args);
				//Reset logging options
				LoggingOptions.disableFlowGroupCompLogging();
				LoggingOptions.setMetricsEnabled(false);
				LoggingOptions.setDbMessageLevel(0);
			}
			catch (Throwable ex)
			{
				logThrowable(ex);
			}

			SwingUtilities.invokeLater(this::enableButtons);
		});
	}

	private void logThrowable(Throwable ex)
	{
		if (ex.getCause() != null)
		{
			logThrowable(ex.getCause());
		}
		LOGGER.log(Level.SEVERE, "Exception occurred", ex);
	}
	
	private void disableButtons()
	{
		for (JButton btn : _buttons)
		{
			btn.setEnabled(false);
		}
	}
	
	private void enableButtons()
	{
		for (JButton btn : _buttons)
		{
			btn.setEnabled(true);
		}
	}
	
	private class ButtonAction extends AbstractAction
	{
		private final String _file;
		public ButtonAction(String name, String file)
		{
			super(name);
			_file = file;
		}

		@Override
		public void actionPerformed(ActionEvent e)
		{
			performHeadless(_file);
		}
	}
}

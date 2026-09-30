package usace.rowcps.headless;

import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.openide.util.lookup.ServiceProvider;
import usace.rowcps.regi.interfaces.progress.IProgressHandle;
import usace.rowcps.regi.interfaces.progress.ProgressService;

/**
 *
 * @author ryan
 */
@ServiceProvider(service = ProgressService.class)
public class HeadlessProgressService implements ProgressService
{

    private static final Logger LOGGER = Logger.getLogger(HeadlessProgressService.class.getName());

    private final List<IProgressHandle> _created;
    private final List<IProgressHandle> _finished;

    public HeadlessProgressService()
    {
        _finished = new ArrayList<>();
        _created = new ArrayList<>();
    }

    @Override
    public IProgressHandle createHandle(String string)
    {
        LOGGER.log(Level.FINE, "Creating progress handle for {0}", string);
        IProgressHandle handleImpl = new HeadlessHandleImpl(string)
        {
            @Override
            public void finish()
            {
                super.finish();
                _finished.add(this);
            }

        };
        _created.add(handleImpl);
        return handleImpl;
    }
}

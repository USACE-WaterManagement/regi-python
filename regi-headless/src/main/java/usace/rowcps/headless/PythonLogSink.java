package usace.rowcps.headless;

import java.util.logging.LogRecord;

public interface PythonLogSink {
    void log(LogRecord record, String message);
}

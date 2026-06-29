package usace.rowcps.headless;

import java.util.logging.ErrorManager;
import java.util.logging.Formatter;
import java.util.logging.Handler;
import java.util.logging.LogRecord;

public final class PythonJulHandler extends Handler {
    
    private final PythonLogSink sink;
    
    private final Formatter messageFormatter = new Formatter() {
        @Override
        public String format(LogRecord record) {
            return formatMessage(record);
        }
    };

    public PythonJulHandler(PythonLogSink sink) {
        this.sink = sink;
    }

    @Override
    public void publish(LogRecord record) {
        if (record == null || !isLoggable(record)) {
            return;
        }

        try {
            String message = messageFormatter.format(record);
            sink.log(record, message);
        } catch (RuntimeException ex) {
            // Safeguard against failures in Python log handling.
            reportError("Failed to publish JUL record to Python logging.", ex, ErrorManager.WRITE_FAILURE);
        }
    }

    @Override
    public void flush() {
        // No-op. Python logging handlers manage their own flushing.
    }

    @Override
    public void close() {
        // No-op.
    }
}

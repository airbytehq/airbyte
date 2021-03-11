package io.airbyte.workers.temporal;

import com.google.common.base.Stopwatch;
import io.airbyte.workers.WorkerException;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import io.temporal.client.ActivityCompletionException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.concurrent.TimeUnit;

public interface CancellationHandler {
    void heartbeat(Runnable callback) throws WorkerException;

    class TemporalCancellationHandler implements CancellationHandler {
        private static final Logger LOGGER = LoggerFactory.getLogger(TemporalCancellationHandler.class);
        private static final Duration INTERVAL = Duration.ofSeconds(5);
        final ActivityExecutionContext context;
        final Stopwatch stopwatch;

        public TemporalCancellationHandler() {
            context = Activity.getExecutionContext();
            stopwatch = Stopwatch.createStarted();
        }

        @Override
        public void heartbeat(Runnable callback) throws WorkerException {
            if(stopwatch.elapsed(TimeUnit.SECONDS) > TimeUnit.SECONDS.convert(INTERVAL)) {
                try {
                    LOGGER.info("heartbeating...");
                    context.heartbeat(null);
                } catch (ActivityCompletionException e) {
                    LOGGER.info("running callback...");
                    callback.run();
                    throw new WorkerException("Sync cancelled", e);
                }
                stopwatch.reset();
                stopwatch.start();
            }
        }
    }
}

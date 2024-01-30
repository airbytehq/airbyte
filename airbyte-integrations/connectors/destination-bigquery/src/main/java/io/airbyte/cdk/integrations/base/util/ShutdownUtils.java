package io.airbyte.cdk.integrations.base.util;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.string.Strings;
import jakarta.inject.Singleton;
import org.apache.commons.lang3.ThreadUtils;
import org.apache.commons.lang3.concurrent.BasicThreadFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.function.Predicate;
import java.util.stream.Collectors;

@Singleton
public class ShutdownUtils {

    private static final Logger LOGGER = LoggerFactory.getLogger(ShutdownUtils.class);

    public static final String TYPE_AND_DEDUPE_THREAD_NAME = "type-and-dedupe";

    public static final int FORCED_EXIT_CODE = 2;

    public static final int EXIT_THREAD_DELAY_MINUTES = 70;

    public static final Runnable EXIT_HOOK = () -> System.exit(FORCED_EXIT_CODE);

    public static final int INTERRUPT_THREAD_DELAY_MINUTES = 60;

    /**
     * Filters threads that should not be considered when looking for orphaned threads at shutdown of
     * the integration runner.
     * <p>
     * </p>
     * <b>N.B.</b> Daemon threads don't block the JVM if the main `currentThread` exits, so they are not
     * problematic. Additionally, ignore database connection pool threads, which stay active so long as
     * the database connection pool is open.
     */
    @VisibleForTesting
    static final Predicate<Thread> ORPHANED_THREAD_FILTER = runningThread -> !runningThread.getName().equals(Thread.currentThread().getName())
            && !runningThread.isDaemon() && !TYPE_AND_DEDUPE_THREAD_NAME.equals(runningThread.getName());

    /**
     * Stops any non-daemon threads that could block the JVM from exiting when the main thread is done.
     * <p>
     * If any active non-daemon threads would be left as orphans, this method will schedule some
     * interrupt/exit hooks after giving it some time delay to close up properly. It is generally
     * preferred to have a proper closing sequence from children threads instead of interrupting or
     * force exiting the process, so this mechanism serve as a fallback while surfacing warnings in logs
     * for maintainers to fix the code behavior instead.
     *
     * @param exitHook The {@link Runnable} exit hook to execute for any orphaned threads.
     * @param interruptTimeDelay The time to delay execution of the orphaned thread interrupt attempt.
     * @param interruptTimeUnit The time unit of the interrupt delay.
     * @param exitTimeDelay The time to delay execution of the orphaned thread exit hook.
     * @param exitTimeUnit The time unit of the exit delay.
     */
    public void stopOrphanedThreads(final Runnable exitHook,
                                    final int interruptTimeDelay,
                                    final TimeUnit interruptTimeUnit,
                                    final int exitTimeDelay,
                                    final TimeUnit exitTimeUnit) {
        final Thread currentThread = Thread.currentThread();

        final List<Thread> runningThreads = ThreadUtils.getAllThreads()
                .stream()
                .filter(ORPHANED_THREAD_FILTER)
                .collect(Collectors.toList());
        if (!runningThreads.isEmpty()) {
            LOGGER.warn("""
                  The main thread is exiting while children non-daemon threads from a connector are still active.
                  Ideally, this situation should not happen...
                  Please check with maintainers if the connector or library code should safely clean up its threads before quitting instead.
                  The main thread is: {}""", dumpThread(currentThread));
            final ScheduledExecutorService scheduledExecutorService = Executors
                    .newSingleThreadScheduledExecutor(new BasicThreadFactory.Builder()
                            // this thread executor will create daemon threads, so it does not block exiting if all other active
                            // threads are already stopped.
                            .daemon(true).build());
            for (final Thread runningThread : runningThreads) {
                final String str = "Active non-daemon thread: " + dumpThread(runningThread);
                LOGGER.warn(str);
                // even though the main thread is already shutting down, we still leave some chances to the children
                // threads to close properly on their own.
                // So, we schedule an interrupt hook after a fixed time delay instead...
                scheduledExecutorService.schedule(runningThread::interrupt, interruptTimeDelay, interruptTimeUnit);
            }
            scheduledExecutorService.schedule(() -> {
                if (ThreadUtils.getAllThreads().stream()
                        .anyMatch(runningThread -> !runningThread.isDaemon() && !runningThread.getName().equals(currentThread.getName()))) {
                    LOGGER.error("Failed to interrupt children non-daemon threads, forcefully exiting NOW...\n");
                    exitHook.run();
                }
            }, exitTimeDelay, exitTimeUnit);
        }
    }

    private String dumpThread(final Thread thread) {
        return String.format("%s (%s)\n Thread stacktrace: %s", thread.getName(), thread.getState(),
                Strings.join(List.of(thread.getStackTrace()), "\n        at "));
    }
}

/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.util

import com.google.common.annotations.VisibleForTesting
import io.airbyte.commons.string.Strings
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.function.Predicate
import java.util.stream.Collectors
import kotlin.system.exitProcess
import org.apache.commons.lang3.ThreadUtils
import org.apache.commons.lang3.concurrent.BasicThreadFactory

private val logger = KotlinLogging.logger {}

/**
 * Collection of utility methods to ensure that any threads launched by a connector are cleaned up
 * when an operation completes.
 */
@Singleton
class ShutdownUtils {
    companion object {
        private const val TYPE_AND_DEDUPE_THREAD_NAME: String = "type-and-dedupe"
        private const val MICRONAUT_SCHEDULER_THREAD_NAME: String = "scheduled-executor-thread"
        private const val FORCED_EXIT_CODE: Int = 2
        const val EXIT_THREAD_DELAY_MINUTES: Int = 70
        val EXIT_HOOK: Runnable = Runnable { exitProcess(FORCED_EXIT_CODE) }
        const val INTERRUPT_THREAD_DELAY_MINUTES: Int = 60

        /**
         * Filters threads that should not be considered when looking for orphaned threads at
         * shutdown of the integration runner.
         *
         * **N.B.** Daemon threads don't block the JVM if the main `currentThread` exits, so they
         * are not problematic. Additionally, ignore database connection pool threads, which stay
         * active so long as the database connection pool is open.
         */
        @VisibleForTesting
        val ORPHANED_THREAD_FILTER: Predicate<Thread> =
            Predicate<Thread> { runningThread: Thread ->
                (runningThread.name != Thread.currentThread().name &&
                    !runningThread.isDaemon &&
                    (TYPE_AND_DEDUPE_THREAD_NAME != runningThread.name &&
                        !runningThread.name.startsWith(MICRONAUT_SCHEDULER_THREAD_NAME)))
            }
    }

    /**
     * Stops any non-daemon threads that could block the JVM from exiting when the main thread is
     * done.
     *
     * If any active non-daemon threads would be left as orphans, this method will schedule some
     * interrupt/exit hooks after giving it some time delay to close up properly. It is generally
     * preferred to have a proper closing sequence from children threads instead of interrupting or
     * force exiting the process, so this mechanism serve as a fallback while surfacing warnings in
     * logs for maintainers to fix the code behavior instead.
     *
     * @param exitHook The [Runnable] exit hook to execute for any orphaned threads.
     * @param interruptTimeDelay The time to delay execution of the orphaned thread interrupt
     * attempt.
     * @param interruptTimeUnit The time unit of the interrupt delay.
     * @param exitTimeDelay The time to delay execution of the orphaned thread exit hook.
     * @param exitTimeUnit The time unit of the exit delay.
     */
    fun stopOrphanedThreads(
        exitHook: Runnable,
        interruptTimeDelay: Int,
        interruptTimeUnit: TimeUnit,
        exitTimeDelay: Int,
        exitTimeUnit: TimeUnit,
    ) {
        val currentThread = Thread.currentThread()

        val runningThreads =
            ThreadUtils.getAllThreads()
                .stream()
                .filter(ORPHANED_THREAD_FILTER)
                .collect(Collectors.toList())
        if (runningThreads.isNotEmpty()) {
            logger.warn {
                """
                The main thread is exiting while children non-daemon threads from a connector are still active.
                Ideally, this situation should not happen...
                Please check with maintainers if the connector or library code should safely clean up its threads before quitting instead.
                The main thread is: ${dumpThread(currentThread)}
                """.trimIndent()
            }
            val scheduledExecutorService =
                Executors.newSingleThreadScheduledExecutor(
                    // this thread executor will create daemon threads, so it does not block exiting
                    // if all other active
                    BasicThreadFactory.Builder()
                        // threads are already stopped.
                        .daemon(true)
                        .build(),
                )
            for (runningThread in runningThreads) {
                val str = "Active non-daemon thread: " + dumpThread(runningThread)
                logger.warn { str }
                // even though the main thread is already shutting down, we still leave some chances
                // to the children
                // threads to close properly on their own.
                // So, we schedule an interrupt hook after a fixed time delay instead...
                scheduledExecutorService.schedule(
                    { runningThread.interrupt() },
                    interruptTimeDelay.toLong(),
                    interruptTimeUnit,
                )
            }
            scheduledExecutorService.schedule(
                {
                    if (
                        ThreadUtils.getAllThreads().stream().anyMatch { runningThread: Thread ->
                            !runningThread.isDaemon && runningThread.name != currentThread.name
                        }
                    ) {
                        logger.error {
                            "Failed to interrupt children non-daemon threads, forcefully exiting NOW...\n"
                        }
                        exitHook.run()
                    }
                },
                exitTimeDelay.toLong(),
                exitTimeUnit
            )
        }
    }

    private fun dumpThread(thread: Thread): String {
        return String.format(
            "%s (%s)\n Thread stacktrace: %s",
            thread.name,
            thread.state,
            Strings.join(listOf(*thread.stackTrace), "\n        at "),
        )
    }
}

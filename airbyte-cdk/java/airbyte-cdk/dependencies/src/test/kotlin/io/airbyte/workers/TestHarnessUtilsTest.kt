/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.workers.internal.HeartbeatMonitor
import io.airbyte.workers.test_utils.TestConfigHelpers
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.time.temporal.ChronoUnit
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import java.util.function.BiConsumer
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.invocation.InvocationOnMock
import org.mockito.kotlin.mock

private val LOGGER = KotlinLogging.logger {}

internal class TestHarnessUtilsTest {
    @Nested
    internal inner class GentleCloseWithHeartbeat {
        private val CHECK_HEARTBEAT_DURATION: Duration = Duration.of(10, ChronoUnit.MILLIS)

        private val SHUTDOWN_TIME_DURATION: Duration = Duration.of(100, ChronoUnit.MILLIS)

        private var process: Process = mock()
        private var heartbeatMonitor: HeartbeatMonitor = mock()
        private var forceShutdown: BiConsumer<Process, Duration> = mock()

        @BeforeEach
        fun setup() {
            process = Mockito.mock(Process::class.java)
            heartbeatMonitor = Mockito.mock(HeartbeatMonitor::class.java)
            forceShutdown = mock()
        }

        private fun runShutdown() {
            gentleCloseWithHeartbeat(
                process,
                heartbeatMonitor,
                SHUTDOWN_TIME_DURATION,
                CHECK_HEARTBEAT_DURATION,
                SHUTDOWN_TIME_DURATION,
                forceShutdown
            )
        }

        // Verify that shutdown waits indefinitely when heartbeat and process are healthy.
        @Test
        @Throws(InterruptedException::class)
        fun testStartsWait() {
            Mockito.`when`(process.isAlive).thenReturn(true)
            val recordedBeats = AtomicInteger(0)
            Mockito.doAnswer { ignored: InvocationOnMock ->
                    recordedBeats.incrementAndGet()
                    true
                }
                .`when`<HeartbeatMonitor>(heartbeatMonitor)
                .isBeating

            val thread = Thread { this.runShutdown() }

            thread.start()

            // block until the loop is running.
            while (recordedBeats.get() < 3) {
                Thread.sleep(10)
            }
        }

        @Test
        fun testGracefulShutdown() {
            Mockito.`when`(heartbeatMonitor.isBeating).thenReturn(false)
            Mockito.`when`(process.isAlive).thenReturn(false)

            runShutdown()

            Mockito.verifyNoInteractions(forceShutdown)
        }

        @Test
        fun testForcedShutdown() {
            Mockito.`when`(heartbeatMonitor.isBeating).thenReturn(false)
            Mockito.`when`(process.isAlive).thenReturn(true)

            runShutdown()

            Mockito.verify(forceShutdown).accept(process, SHUTDOWN_TIME_DURATION)
        }

        @Test
        fun testProcessDies() {
            Mockito.`when`(heartbeatMonitor.isBeating).thenReturn(true)
            Mockito.`when`(process.isAlive).thenReturn(false)
            runShutdown()

            Mockito.verifyNoInteractions(forceShutdown)
        }
    }

    @Test
    fun testMapStreamNamesToSchemasWithNullNamespace() {
        val syncPair = TestConfigHelpers.createSyncConfig()
        val syncInput = syncPair.value
        val mapOutput = TestHarnessUtils.mapStreamNamesToSchemas(syncInput)
        Assertions.assertNotNull(
            mapOutput[AirbyteStreamNameNamespacePair("user_preferences", null)]
        )
    }

    @Test
    fun testMapStreamNamesToSchemasWithMultipleNamespaces() {
        val syncPair = TestConfigHelpers.createSyncConfig(true)
        val syncInput = syncPair.value
        val mapOutput = TestHarnessUtils.mapStreamNamesToSchemas(syncInput)
        Assertions.assertNotNull(
            mapOutput[AirbyteStreamNameNamespacePair("user_preferences", "namespace")]
        )
        Assertions.assertNotNull(
            mapOutput[AirbyteStreamNameNamespacePair("user_preferences", "namespace2")]
        )
    }

    companion object {

        /**
         * As long as the the heartbeatMonitor detects a heartbeat, the process will be allowed to
         * continue. This method checks the heartbeat once every minute. Once there is no heartbeat
         * detected, if the process has ended, then the method returns. If the process is still
         * running it is given a grace period of the timeout arguments passed into the method. Once
         * those expire the process is killed forcibly. If the process cannot be killed, this method
         * will log that this is the case, but then returns.
         *
         * @param process
         * - process to monitor.
         * @param heartbeatMonitor
         * - tracks if the heart is still beating for the given process.
         * @param gracefulShutdownDuration
         * - grace period to give the process to die after its heart stops beating.
         * @param checkHeartbeatDuration
         * - frequency with which the heartbeat of the process is checked.
         * @param forcedShutdownDuration
         * - amount of time to wait if a process needs to be destroyed forcibly.
         */
        fun gentleCloseWithHeartbeat(
            process: Process,
            heartbeatMonitor: HeartbeatMonitor,
            gracefulShutdownDuration: Duration,
            checkHeartbeatDuration: Duration,
            forcedShutdownDuration: Duration,
            forceShutdown: BiConsumer<Process, Duration>
        ) {
            while (process.isAlive && heartbeatMonitor.isBeating) {
                try {
                    process.waitFor(checkHeartbeatDuration.toMillis(), TimeUnit.MILLISECONDS)
                } catch (e: InterruptedException) {
                    LOGGER.error(e) { "Exception while waiting for process to finish" }
                }
            }

            if (process.isAlive) {
                try {
                    process.waitFor(gracefulShutdownDuration.toMillis(), TimeUnit.MILLISECONDS)
                } catch (e: InterruptedException) {
                    LOGGER.error {
                        "Exception during grace period for process to finish. This can happen when cancelling jobs."
                    }
                }
            }

            // if we were unable to exist gracefully, force shutdown...
            if (process.isAlive) {
                forceShutdown.accept(process, forcedShutdownDuration)
            }
        }
    }
}

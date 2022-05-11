/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.workers.protocols.airbyte.HeartbeatMonitor;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiConsumer;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class WorkerUtilsTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(GentleCloseWithHeartbeat.class);

  @Nested
  class GentleCloseWithHeartbeat {

    private final Duration CHECK_HEARTBEAT_DURATION = Duration.of(10, ChronoUnit.MILLIS);

    private final Duration SHUTDOWN_TIME_DURATION = Duration.of(100, ChronoUnit.MILLIS);

    private Process process;
    private HeartbeatMonitor heartbeatMonitor;
    private BiConsumer<Process, Duration> forceShutdown;

    @SuppressWarnings("unchecked")
    @BeforeEach
    void setup() {
      process = mock(Process.class);
      heartbeatMonitor = mock(HeartbeatMonitor.class);
      forceShutdown = mock(BiConsumer.class);
    }

    private void runShutdown() {
      gentleCloseWithHeartbeat(
          new WorkerConfigs(new EnvConfigs()),
          process,
          heartbeatMonitor,
          SHUTDOWN_TIME_DURATION,
          CHECK_HEARTBEAT_DURATION,
          SHUTDOWN_TIME_DURATION,
          forceShutdown);
    }

    @SuppressWarnings("BusyWait")
    @DisplayName("Verify that shutdown waits indefinitely when heartbeat and process are healthy.")
    @Test
    void testStartsWait() throws InterruptedException {
      when(process.isAlive()).thenReturn(true);
      final AtomicInteger recordedBeats = new AtomicInteger(0);
      doAnswer((ignored) -> {
        recordedBeats.incrementAndGet();
        return true;
      }).when(heartbeatMonitor).isBeating();

      final Thread thread = new Thread(this::runShutdown);

      thread.start();

      // block until the loop is running.
      while (recordedBeats.get() < 3) {
        Thread.sleep(10);
      }

      thread.stop();
    }

    @Test
    @DisplayName("Test heartbeat ends and graceful shutdown.")
    void testGracefulShutdown() {
      when(heartbeatMonitor.isBeating()).thenReturn(false);
      when(process.isAlive()).thenReturn(false);

      runShutdown();

      verifyNoInteractions(forceShutdown);
    }

    @Test
    @DisplayName("Test heartbeat ends and shutdown is forced.")
    void testForcedShutdown() {
      when(heartbeatMonitor.isBeating()).thenReturn(false);
      when(process.isAlive()).thenReturn(true);

      runShutdown();

      verify(forceShutdown).accept(process, SHUTDOWN_TIME_DURATION);
    }

    @Test
    @DisplayName("Test process dies.")
    void testProcessDies() {
      when(heartbeatMonitor.isBeating()).thenReturn(true);
      when(process.isAlive()).thenReturn(false);
      runShutdown();

      verifyNoInteractions(forceShutdown);
    }

  }

  @Test
  void testMapStreamNamesToSchemasWithNullNamespace() {
    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig();
    final StandardSyncInput syncInput = syncPair.getValue();
    final Map<String, JsonNode> mapOutput = WorkerUtils.mapStreamNamesToSchemas(syncInput);
    assertNotNull(mapOutput.get("user_preferences"));
  }

  @Test
  void testMapStreamNamesToSchemasWithMultipleNamespaces() {
    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig(true);
    final StandardSyncInput syncInput = syncPair.getValue();
    final Map<String, JsonNode> mapOutput = WorkerUtils.mapStreamNamesToSchemas(syncInput);
    assertNotNull(mapOutput.get("namespaceuser_preferences"));
    assertNotNull(mapOutput.get("namespace2user_preferences"));
  }

  /**
   * As long as the the heartbeatMonitor detects a heartbeat, the process will be allowed to continue.
   * This method checks the heartbeat once every minute. Once there is no heartbeat detected, if the
   * process has ended, then the method returns. If the process is still running it is given a grace
   * period of the timeout arguments passed into the method. Once those expire the process is killed
   * forcibly. If the process cannot be killed, this method will log that this is the case, but then
   * returns.
   *
   * @param process - process to monitor.
   * @param heartbeatMonitor - tracks if the heart is still beating for the given process.
   * @param gracefulShutdownDuration - grace period to give the process to die after its heart stops
   *        beating.
   * @param checkHeartbeatDuration - frequency with which the heartbeat of the process is checked.
   * @param forcedShutdownDuration - amount of time to wait if a process needs to be destroyed
   *        forcibly.
   */
  static void gentleCloseWithHeartbeat(final WorkerConfigs workerConfigs,
                                       final Process process,
                                       final HeartbeatMonitor heartbeatMonitor,
                                       final Duration gracefulShutdownDuration,
                                       final Duration checkHeartbeatDuration,
                                       final Duration forcedShutdownDuration,
                                       final BiConsumer<Process, Duration> forceShutdown) {
    while (process.isAlive() && heartbeatMonitor.isBeating()) {
      try {
        if (workerConfigs.getWorkerEnvironment().equals(Configs.WorkerEnvironment.KUBERNETES)) {
          LOGGER.debug("Gently closing process {} with heartbeat..", process.info().commandLine().get());
        }

        process.waitFor(checkHeartbeatDuration.toMillis(), TimeUnit.MILLISECONDS);
      } catch (final InterruptedException e) {
        LOGGER.error("Exception while waiting for process to finish", e);
      }
    }

    if (process.isAlive()) {
      try {
        if (workerConfigs.getWorkerEnvironment().equals(Configs.WorkerEnvironment.KUBERNETES)) {
          LOGGER.debug("Gently closing process {} without heartbeat..", process.info().commandLine().get());
        }

        process.waitFor(gracefulShutdownDuration.toMillis(), TimeUnit.MILLISECONDS);
      } catch (final InterruptedException e) {
        LOGGER.error("Exception during grace period for process to finish. This can happen when cancelling jobs.");
      }
    }

    // if we were unable to exist gracefully, force shutdown...
    if (process.isAlive()) {
      if (workerConfigs.getWorkerEnvironment().equals(Configs.WorkerEnvironment.KUBERNETES)) {
        LOGGER.debug("Force shutdown process {}..", process.info().commandLine().get());
      }

      forceShutdown.accept(process, forcedShutdownDuration);
    }
  }

}

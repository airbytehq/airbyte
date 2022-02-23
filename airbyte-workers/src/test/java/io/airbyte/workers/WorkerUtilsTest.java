/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import io.airbyte.workers.protocols.airbyte.HeartbeatMonitor;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class WorkerUtilsTest {

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
      WorkerUtils.gentleCloseWithHeartbeat(
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

}

/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.workers;

import static org.mockito.Mockito.*;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.workers.protocols.airbyte.HeartbeatMonitor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.logging.log4j.util.TriConsumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class WorkerUtilsTest {

  @Nested
  class GentleCloseWithHeartbeat {

    private final long CHECK_HEARTBEAT_TIME_MAGNITUDE = 10;
    private final TimeUnit CHECK_HEARTBEAT_TIME_UNIT = TimeUnit.MILLISECONDS;

    private final long SHUTDOWN_TIME_MAGNITUDE = 100;
    private final TimeUnit SHUTDOWN_TIME_UNIT = TimeUnit.MILLISECONDS;

    private Process process;
    private HeartbeatMonitor heartbeatMonitor;
    private TriConsumer<Process, Long, TimeUnit> forceShutdown;

    @SuppressWarnings("unchecked")
    @BeforeEach
    void setup() {
      process = mock(Process.class);
      heartbeatMonitor = mock(HeartbeatMonitor.class);
      forceShutdown = mock(TriConsumer.class);
    }

    private void runShutdown() {
      WorkerUtils.gentleCloseWithHeartbeat(
          process,
          heartbeatMonitor,
          SHUTDOWN_TIME_MAGNITUDE,
          SHUTDOWN_TIME_UNIT,
          CHECK_HEARTBEAT_TIME_MAGNITUDE,
          CHECK_HEARTBEAT_TIME_UNIT,
          SHUTDOWN_TIME_MAGNITUDE,
          SHUTDOWN_TIME_UNIT,
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

      verify(forceShutdown).accept(process, SHUTDOWN_TIME_MAGNITUDE, SHUTDOWN_TIME_UNIT);
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

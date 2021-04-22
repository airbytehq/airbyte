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

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.*;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.workers.protocols.airbyte.HeartbeatMonitor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
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
    private AtomicBoolean hasCompleted;
    private AtomicBoolean threwException;
    private Thread gentleCloseThread;
    private TriConsumer<Process, Long, TimeUnit> forceShutdown;

    @SuppressWarnings("unchecked")
    @BeforeEach
    void setup() throws InterruptedException {
      process = mock(Process.class);
      heartbeatMonitor = mock(HeartbeatMonitor.class);
      forceShutdown = mock(TriConsumer.class);
      threwException = new AtomicBoolean(false);
      hasCompleted = new AtomicBoolean(false);
      gentleCloseThread = start(process, heartbeatMonitor, hasCompleted, forceShutdown);
    }

    @SuppressWarnings("BusyWait")
    private Thread start(final Process process,
                         final HeartbeatMonitor heartbeatMonitor,
                         final AtomicBoolean hasCompleted,
                         final TriConsumer<Process, Long, TimeUnit> forceShutdown)
        throws InterruptedException {
      when(process.isAlive()).thenReturn(true);
      final AtomicInteger recordedBeats = new AtomicInteger(0);
      doAnswer((ignored) -> {
        recordedBeats.incrementAndGet();
        return true;
      }).when(heartbeatMonitor).isBeating();

      final Thread thread = new Thread(() -> {
        try {

          WorkerUtils.gentleCloseWithHeartbeat(
              process,
              heartbeatMonitor,
              SHUTDOWN_TIME_MAGNITUDE * 10,
              SHUTDOWN_TIME_UNIT,
              CHECK_HEARTBEAT_TIME_MAGNITUDE,
              CHECK_HEARTBEAT_TIME_UNIT,
              SHUTDOWN_TIME_MAGNITUDE,
              SHUTDOWN_TIME_UNIT,
              forceShutdown);

          hasCompleted.set(true);
        } catch (Throwable e) {
          threwException.set(true);
        }
      });

      thread.start();

      // block until the loop is running.
      while (recordedBeats.get() == 0) {
        Thread.sleep(10);
      }

      return thread;
    }

    @Test
    @DisplayName("Test heartbeat ends and graceful shutdown.")
    void testGracefulShutdown() throws InterruptedException {
      when(heartbeatMonitor.isBeating()).thenReturn(false);
      when(process.isAlive()).thenReturn(false);

      gentleCloseThread.join(0);

      assertFalse(threwException.get());
      assertTrue(hasCompleted.get());
      assertFalse(gentleCloseThread.isAlive());
      verifyNoInteractions(forceShutdown);
    }

    @Test
    @DisplayName("Test heartbeat ends and shutdown is forced.")
    void testForcedShutdown() throws InterruptedException {
      when(heartbeatMonitor.isBeating()).thenReturn(false);
      when(process.isAlive()).thenReturn(true);

      gentleCloseThread.join(0);

      assertFalse(threwException.get());
      assertTrue(hasCompleted.get());
      assertFalse(gentleCloseThread.isAlive());
      verify(forceShutdown).accept(process, SHUTDOWN_TIME_MAGNITUDE, SHUTDOWN_TIME_UNIT);
    }

    @Test
    @DisplayName("Test process dies.")
    void testProcessDies() throws InterruptedException {
      when(process.isAlive()).thenReturn(false);

      gentleCloseThread.join(0);

      assertFalse(threwException.get());
      assertTrue(hasCompleted.get());
      assertFalse(gentleCloseThread.isAlive());
      verifyNoInteractions(forceShutdown);
    }

  }

}

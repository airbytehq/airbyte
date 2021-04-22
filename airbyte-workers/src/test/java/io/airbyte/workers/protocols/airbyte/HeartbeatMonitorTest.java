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

package io.airbyte.workers.protocols.airbyte;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class HeartbeatMonitorTest {

  private static final Instant NOW = Instant.now();
  private static final Instant FIVE_SECONDS_BEFORE = NOW.minus(5, ChronoUnit.SECONDS);
  private static final Instant THIRTY_ONE_SECONDS_BEFORE = NOW.minus(30, ChronoUnit.SECONDS);

  private Supplier<Instant> instantSupplier;
  private HeartbeatMonitor heartbeatMonitor;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() {
    instantSupplier = mock(Supplier.class);
    heartbeatMonitor = new HeartbeatMonitor(instantSupplier);
  }

  @Test
  void testNeverBeat() {
    assertFalse(heartbeatMonitor.isBeating());
  }

  @Test
  void testRecentBeat() {
    when(instantSupplier.get()).thenReturn(FIVE_SECONDS_BEFORE).thenReturn(NOW);
    assertTrue(heartbeatMonitor.isBeating());
  }

  @Test
  void testStaleBeat() {
    when(instantSupplier.get()).thenReturn(THIRTY_ONE_SECONDS_BEFORE).thenReturn(NOW);
    assertFalse(heartbeatMonitor.isBeating());
  }

}

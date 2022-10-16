/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class HeartbeatMonitorTest {

  private static final Duration HEART_BEAT_FRESH_DURATION = Duration.of(30, ChronoUnit.SECONDS);

  private static final Instant NOW = Instant.now();
  private static final Instant FIVE_SECONDS_BEFORE = NOW.minus(5, ChronoUnit.SECONDS);
  private static final Instant THIRTY_SECONDS_BEFORE = NOW.minus(30, ChronoUnit.SECONDS);

  private Supplier<Instant> nowSupplier;
  private HeartbeatMonitor heartbeatMonitor;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() {
    nowSupplier = mock(Supplier.class);
    heartbeatMonitor = new HeartbeatMonitor(HEART_BEAT_FRESH_DURATION, nowSupplier);
  }

  @Test
  void testNeverBeat() {
    assertFalse(heartbeatMonitor.isBeating());
  }

  @Test
  void testFreshBeat() {
    when(nowSupplier.get()).thenReturn(FIVE_SECONDS_BEFORE).thenReturn(NOW);
    heartbeatMonitor.beat();
    assertTrue(heartbeatMonitor.isBeating());
  }

  @Test
  void testStaleBeat() {
    when(nowSupplier.get()).thenReturn(THIRTY_SECONDS_BEFORE).thenReturn(NOW);
    heartbeatMonitor.beat();
    assertFalse(heartbeatMonitor.isBeating());
  }

}

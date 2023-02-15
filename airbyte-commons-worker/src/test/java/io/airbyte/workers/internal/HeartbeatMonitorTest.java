/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.time.Duration;
import java.time.Instant;
import java.util.function.Supplier;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class HeartbeatMonitorTest {

  private static final Duration HEART_BEAT_FRESH_DURATION = Duration.ofSeconds(30);

  private static final Instant NOW = Instant.now();
  private static final Instant FIVE_SECONDS_BEFORE = NOW.minusSeconds(5);
  private static final Instant THIRTY_SECONDS_BEFORE = NOW.minusSeconds(30);

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
    Assertions.assertThat(heartbeatMonitor.isBeating()).isEmpty();
  }

  @Test
  void testFreshBeat() {
    when(nowSupplier.get()).thenReturn(FIVE_SECONDS_BEFORE).thenReturn(NOW);
    heartbeatMonitor.beat();
    Assertions.assertThat(heartbeatMonitor.getTimeSinceLastBeat()).hasValue(Duration.ofSeconds(5));
    Assertions.assertThat(heartbeatMonitor.isBeating()).hasValue(true);
  }

  @Test
  void testStaleBeat() {
    when(nowSupplier.get()).thenReturn(THIRTY_SECONDS_BEFORE).thenReturn(NOW);
    heartbeatMonitor.beat();
    Assertions.assertThat(heartbeatMonitor.getTimeSinceLastBeat()).hasValue(Duration.ofSeconds(30));
    Assertions.assertThat(heartbeatMonitor.isBeating()).hasValue(false);
  }

}

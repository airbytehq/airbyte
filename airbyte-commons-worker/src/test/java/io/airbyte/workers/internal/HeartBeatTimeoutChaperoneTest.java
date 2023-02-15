/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.featureflag.FeatureFlagClient;
import io.airbyte.featureflag.TestClient;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class HeartBeatTimeoutChaperoneTest {

  private final HeartbeatMonitor heartbeatMonitor = mock(HeartbeatMonitor.class);
  private final Duration timeoutCheckDuration = Duration.ofMillis(1);

  private final Map<String, Boolean> flags = new HashMap<>();
  private final FeatureFlagClient featureFlagClient = new TestClient(flags);
  private final UUID workspaceId = UUID.randomUUID();
  private final ExecutorService executorService = Executors.newFixedThreadPool(4);

  private final HeartbeatTimeoutChaperone heartbeatTimeoutChaperone = new HeartbeatTimeoutChaperone(
      heartbeatMonitor,
      timeoutCheckDuration,
      featureFlagClient,
      workspaceId);

  @BeforeEach
  void init() {
    flags.clear();
  }

  @Test
  void testFailHeartbeat() {
    flags.put("heartbeat.failSync", true);
    when(heartbeatMonitor.isBeating()).thenReturn(Optional.of(false));
    assertThrows(HeartbeatTimeoutChaperone.HeartbeatTimeoutException.class,
        () -> heartbeatTimeoutChaperone.runWithHeartbeatThread(() -> {
          try {
            Thread.sleep(Long.MAX_VALUE);
          } catch (final InterruptedException e) {
            throw new RuntimeException(e);
          }
        }, executorService).run());
  }

  @Test
  void testNotFailingHeartbeat() {
    flags.put("heartbeat.failSync", true);
    when(heartbeatMonitor.isBeating()).thenReturn(Optional.of(true));
    assertDoesNotThrow(() -> heartbeatTimeoutChaperone.runWithHeartbeatThread(() -> {
      try {
        Thread.sleep(10);
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      }
    }, executorService).run());
  }

  @Test
  void testFailHeartbeatWithoutFeatureFlag() {
    flags.put("heartbeat.failSync", false);
    when(heartbeatMonitor.isBeating()).thenReturn(Optional.of(false));
    assertDoesNotThrow(() -> heartbeatTimeoutChaperone.runWithHeartbeatThread(() -> {
      try {
        Thread.sleep(100);
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      }
    }, executorService).run());
  }

}

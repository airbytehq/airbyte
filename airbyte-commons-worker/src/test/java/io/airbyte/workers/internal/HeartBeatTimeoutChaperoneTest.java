/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.featureflag.FeatureFlagClient;
import io.airbyte.featureflag.ShouldFailSyncIfHeartbeatFailure;
import io.airbyte.featureflag.TestClient;
import java.time.Duration;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.junit.jupiter.api.Test;

class HeartBeatTimeoutChaperoneTest {

  private final HeartbeatMonitor heartbeatMonitor = mock(HeartbeatMonitor.class);
  private final Duration timeoutCheckDuration = Duration.ofMillis(1);

  private final FeatureFlagClient featureFlagClient = mock(TestClient.class);
  private final UUID workspaceId = UUID.randomUUID();

  @Test
  void testFailHeartbeat() {
    final HeartbeatTimeoutChaperone heartbeatTimeoutChaperone = new HeartbeatTimeoutChaperone(
        heartbeatMonitor,
        timeoutCheckDuration,
        featureFlagClient,
        workspaceId,
        Optional.of(() -> {}));
    assertThrows(HeartbeatTimeoutChaperone.HeartbeatTimeoutException.class,
        () -> heartbeatTimeoutChaperone.runWithHeartbeatThread(() -> {
          try {
            Thread.sleep(Long.MAX_VALUE);
          } catch (final InterruptedException e) {
            throw new RuntimeException(e);
          }
        }).run());
  }

  @Test
  void testNotFailingHeartbeat() {
    final HeartbeatTimeoutChaperone heartbeatTimeoutChaperone = new HeartbeatTimeoutChaperone(
        heartbeatMonitor,
        timeoutCheckDuration,
        featureFlagClient,
        workspaceId,
        Optional.of(() -> {
          try {
            Thread.sleep(Long.MAX_VALUE);
          } catch (final InterruptedException e) {
            throw new RuntimeException(e);
          }
        }));
    assertDoesNotThrow(() -> heartbeatTimeoutChaperone.runWithHeartbeatThread(() -> {}).run());
  }

  @Test
  void testMonitor() {
    final HeartbeatTimeoutChaperone heartbeatTimeoutChaperone = new HeartbeatTimeoutChaperone(
        heartbeatMonitor,
        timeoutCheckDuration,
        featureFlagClient,
        workspaceId);
    when(featureFlagClient.enabled(eq(ShouldFailSyncIfHeartbeatFailure.INSTANCE), any())).thenReturn(true);
    when(heartbeatMonitor.isBeating()).thenReturn(Optional.of(false));
    assertDoesNotThrow(() -> CompletableFuture.runAsync(() -> heartbeatTimeoutChaperone.monitor()).get(1000, TimeUnit.MILLISECONDS));
  }

  @Test
  void testMonitorDontFailIfNoFlag() {
    final HeartbeatTimeoutChaperone heartbeatTimeoutChaperone = new HeartbeatTimeoutChaperone(
        heartbeatMonitor,
        timeoutCheckDuration,
        featureFlagClient,
        workspaceId);
    when(featureFlagClient.enabled(eq(ShouldFailSyncIfHeartbeatFailure.INSTANCE), any())).thenReturn(false);
    when(heartbeatMonitor.isBeating()).thenReturn(Optional.of(true), Optional.of(false));
    assertThrows(TimeoutException.class, () -> CompletableFuture.runAsync(() -> heartbeatTimeoutChaperone.monitor()).get(1000, TimeUnit.MILLISECONDS));
  }

}

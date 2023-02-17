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
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

class HeartBeatTimeoutChaperoneTest {

  private final HeartbeatMonitor heartbeatMonitor = mock(HeartbeatMonitor.class);
  private final Duration timeoutCheckDuration = Duration.ofMillis(1);

  private final FeatureFlagClient featureFlagClient = mock(TestClient.class);
  private final UUID workspaceId = UUID.randomUUID();

  @Test
  void testFailHeartbeat() {
    when(featureFlagClient.enabled(eq(ShouldFailSyncIfHeartbeatFailure.INSTANCE), any())).thenReturn(true);
    final HeartbeatTimeoutChaperone heartbeatTimeoutChaperone = new HeartbeatTimeoutChaperone(
        heartbeatMonitor,
        timeoutCheckDuration,
        featureFlagClient,
        workspaceId,
        Optional.of(() -> {}));

    Assertions.assertThatThrownBy(() -> heartbeatTimeoutChaperone.runWithHeartbeatThread(CompletableFuture.runAsync(() -> {
      try {
        Thread.sleep(Long.MAX_VALUE);
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      }
    })).get())
        .hasCauseInstanceOf(HeartbeatTimeoutChaperone.HeartbeatTimeoutException.class);

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
    assertDoesNotThrow(() -> heartbeatTimeoutChaperone.runWithHeartbeatThread(CompletableFuture.runAsync(() -> {})).get());
  }

  @Test
  void testNotFailingHeartbeatIfFalseFlag() {
    when(featureFlagClient.enabled(eq(ShouldFailSyncIfHeartbeatFailure.INSTANCE), any())).thenReturn(false);
    final HeartbeatTimeoutChaperone heartbeatTimeoutChaperone = new HeartbeatTimeoutChaperone(
        heartbeatMonitor,
        timeoutCheckDuration,
        featureFlagClient,
        workspaceId,
        Optional.of(() -> {}));
    assertDoesNotThrow(() -> heartbeatTimeoutChaperone.runWithHeartbeatThread(CompletableFuture.runAsync(() -> {
      try {
        Thread.sleep(1000);
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      }
    })).get());
  }

  @Test
  void testMonitor() {
    final HeartbeatTimeoutChaperone heartbeatTimeoutChaperone = new HeartbeatTimeoutChaperone(
        heartbeatMonitor,
        timeoutCheckDuration,
        featureFlagClient,
        workspaceId);
    when(heartbeatMonitor.isBeating()).thenReturn(Optional.of(false));
    assertDoesNotThrow(() -> CompletableFuture.runAsync(() -> heartbeatTimeoutChaperone.monitor()).get(1000, TimeUnit.MILLISECONDS));
  }

  @Test
  void testMonitorDontFailIfDontStopBeating() {
    final HeartbeatTimeoutChaperone heartbeatTimeoutChaperone = new HeartbeatTimeoutChaperone(
        heartbeatMonitor,
        timeoutCheckDuration,
        featureFlagClient,
        workspaceId);
    when(heartbeatMonitor.isBeating()).thenReturn(Optional.of(true), Optional.of(true));
    assertThrows(TimeoutException.class,
        () -> CompletableFuture.runAsync(() -> heartbeatTimeoutChaperone.monitor()).get(1000, TimeUnit.MILLISECONDS));
  }

}

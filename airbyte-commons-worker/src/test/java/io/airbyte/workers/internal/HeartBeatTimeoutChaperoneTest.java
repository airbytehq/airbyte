/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.featureflag.FeatureFlagClient;
import io.airbyte.featureflag.ShouldFailSyncIfHeartbeatFailure;
import io.airbyte.featureflag.TestClient;
import io.airbyte.metrics.lib.MetricAttribute;
import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import java.time.Duration;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

class HeartBeatTimeoutChaperoneTest {

  private final HeartbeatMonitor heartbeatMonitor = mock(HeartbeatMonitor.class);
  private final Duration timeoutCheckDuration = Duration.ofMillis(1);

  private final FeatureFlagClient featureFlagClient = mock(TestClient.class);
  private final UUID workspaceId = UUID.randomUUID();
  private final UUID connectionId = UUID.randomUUID();
  private final MetricClient metricClient = mock(MetricClient.class);

  @Test
  void testFailHeartbeat() {
    when(featureFlagClient.enabled(eq(ShouldFailSyncIfHeartbeatFailure.INSTANCE), any())).thenReturn(true);
    final HeartbeatTimeoutChaperone heartbeatTimeoutChaperone = new HeartbeatTimeoutChaperone(
        heartbeatMonitor,
        timeoutCheckDuration,
        featureFlagClient,
        workspaceId,
        Optional.of(() -> {}),
        connectionId,
        metricClient);

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
        }),
        connectionId,
        metricClient);
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
        Optional.of(() -> {}),
        connectionId,
        metricClient);
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
        workspaceId,
        connectionId,
        metricClient);
    when(featureFlagClient.enabled(eq(ShouldFailSyncIfHeartbeatFailure.INSTANCE), any())).thenReturn(true);

    when(heartbeatMonitor.isBeating()).thenReturn(Optional.of(false));

    assertDoesNotThrow(() -> CompletableFuture.runAsync(() -> heartbeatTimeoutChaperone.monitor()).get(1000, TimeUnit.MILLISECONDS));
    verify(metricClient, times(1)).count(OssMetricsRegistry.SOURCE_HEARTBEAT_FAILURE, 1,
        new MetricAttribute(MetricTags.CONNECTION_ID, connectionId.toString()));
  }

  @Test
  void testMonitorDontFailIfDontStopBeating() {
    final HeartbeatTimeoutChaperone heartbeatTimeoutChaperone = new HeartbeatTimeoutChaperone(
        heartbeatMonitor,
        timeoutCheckDuration,
        featureFlagClient,
        workspaceId,
        connectionId,
        metricClient);
    when(featureFlagClient.enabled(eq(ShouldFailSyncIfHeartbeatFailure.INSTANCE), any())).thenReturn(false);
    when(heartbeatMonitor.isBeating()).thenReturn(Optional.of(true), Optional.of(false));

    assertDoesNotThrow(() -> CompletableFuture.runAsync(() -> heartbeatTimeoutChaperone.monitor()).get(1000, TimeUnit.MILLISECONDS));
  }

}

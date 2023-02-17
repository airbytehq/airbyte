/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static java.lang.Thread.sleep;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.featureflag.FeatureFlagClient;
import io.airbyte.featureflag.ShouldFailSyncIfHeartbeatFailure;
import io.airbyte.featureflag.Workspace;
import io.airbyte.metrics.lib.MetricAttribute;
import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import java.time.Duration;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The {@link HeartbeatTimeoutChaperone} takes in an arbitrary runnable and a heartbeat monitor. It
 * runs each in separate threads. If the heartbeat monitor thread completes before the runnable,
 * that means that the heartbeat has stopped. If this occurs the chaperone cancels the runnable
 * thread and then throws an exception. If the runnable thread completes first, the chaperone
 * cancels the heartbeat and then returns.
 *
 * This allows us to run an arbitrary runnable that we can kill if a heartbeat stops. This is useful
 * in cases like the platform reading from the source. The thread that reads from the source is
 * allowed to run as long as the heartbeat from the sources is fresh.
 */
public class HeartbeatTimeoutChaperone {

  private static final Logger LOGGER = LoggerFactory.getLogger(HeartbeatTimeoutChaperone.class);

  public static final Duration DEFAULT_TIMEOUT_CHECK_DURATION = Duration.ofSeconds(1);

  private final HeartbeatMonitor heartbeatMonitor;
  private final Duration timeoutCheckDuration;
  private final FeatureFlagClient featureFlagClient;
  private final UUID workspaceId;
  private final ExecutorService executorService = Executors.newFixedThreadPool(2);
  private final Optional<Runnable> customMonitor;
  private final UUID connectionId;
  private final MetricClient metricClient;

  public HeartbeatTimeoutChaperone(final HeartbeatMonitor heartbeatMonitor,
                                   final Duration timeoutCheckDuration,
                                   final FeatureFlagClient featureFlagClient,
                                   final UUID workspaceId,
                                   final UUID connectionId,
                                   final MetricClient metricClient) {
    this.timeoutCheckDuration = timeoutCheckDuration;

    this.heartbeatMonitor = heartbeatMonitor;
    this.featureFlagClient = featureFlagClient;
    this.workspaceId = workspaceId;
    this.connectionId = connectionId;
    this.metricClient = metricClient;
    this.customMonitor = Optional.empty();
  }

  @VisibleForTesting
  HeartbeatTimeoutChaperone(final HeartbeatMonitor heartbeatMonitor,
                            final Duration timeoutCheckDuration,
                            final FeatureFlagClient featureFlagClient,
                            final UUID workspaceId,
                            final Optional<Runnable> customMonitor,
                            final UUID connectionId,
                            final MetricClient metricClient) {
    this.timeoutCheckDuration = timeoutCheckDuration;

    this.heartbeatMonitor = heartbeatMonitor;
    this.featureFlagClient = featureFlagClient;
    this.workspaceId = workspaceId;
    this.connectionId = connectionId;
    this.metricClient = metricClient;
    this.customMonitor = customMonitor;
  }

  public CompletableFuture runWithHeartbeatThread(final CompletableFuture<Void> runnableFuture) throws InterruptedException {
    LOGGER.info("Starting source heartbeat check. Will check every {} minutes.", timeoutCheckDuration.toMinutes());
    final CompletableFuture<Void> heartbeatFuture = CompletableFuture.runAsync(customMonitor.orElse(this::monitor), executorService);

    try {
      CompletableFuture.anyOf(runnableFuture, heartbeatFuture).get();
    } catch (final InterruptedException e) {
      LOGGER.error("Heartbeat chaperone thread was interrupted.", e);
      return getContinue();
    } catch (final ExecutionException e) {
      // this should check explicitly for source and destination exceptions
      if (e.getCause() instanceof RuntimeException) {
        return raiseException((RuntimeException) e.getCause());
      } else {
        return raiseException(new RuntimeException(e));
      }
    }

    LOGGER.info("thread status... heartbeat thread: {} , replication thread: {}", heartbeatFuture.isDone(), runnableFuture.isDone());

    if (heartbeatFuture.isDone() && !runnableFuture.isDone()) {
      if (featureFlagClient.enabled(ShouldFailSyncIfHeartbeatFailure.INSTANCE, new Workspace(workspaceId))) {
        runnableFuture.cancel(true);
        return raiseException(
            new HeartbeatTimeoutException(String.format("Heartbeat has stopped. Heartbeat freshness threshold: %s secs Actual heartbeat age: %s secs",
                heartbeatMonitor.getHeartbeatFreshnessThreshold().getSeconds(),
                heartbeatMonitor.getTimeSinceLastBeat().orElse(Duration.ZERO).getSeconds())));
      } else {
        LOGGER.info("Do not return because the feature flag is disable");
        return runnableFuture;
      }
    }

    heartbeatFuture.cancel(true);

    return getContinue();
  }

  @SuppressWarnings("BusyWait")
  @VisibleForTesting
  void monitor() {
    while (true) {
      try {
        sleep(timeoutCheckDuration.toMillis());
      } catch (final InterruptedException e) {
        LOGGER.info("Stopping the heartbeat monitor");
        return;
      }

      // if not beating, return. otherwise, if it is beating or heartbeat hasn't started, continue.
      if (!heartbeatMonitor.isBeating().orElse(true)) {
        metricClient.count(OssMetricsRegistry.SOURCE_HEARTBEAT_FAILURE, 1,
            new MetricAttribute(MetricTags.CONNECTION_ID, connectionId.toString()));
        LOGGER.error("Source has stopped heart beating.");
        return;
      }
    }
  }

  private CompletableFuture getContinue() {
    return CompletableFuture.runAsync(() -> {}, executorService);
  }

  private CompletableFuture raiseException(final RuntimeException e) {
    return CompletableFuture.runAsync(() -> {
      throw e;
    }, executorService);
  }

  public static class HeartbeatTimeoutException extends RuntimeException {

    public HeartbeatTimeoutException(final String message) {
      super(message);
    }

  }

}

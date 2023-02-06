/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.featureflag.FeatureFlagClient;
import io.airbyte.featureflag.ShouldFailSyncIfHeartbeatFailure;
import io.airbyte.featureflag.Workspace;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;

import static java.lang.Thread.sleep;

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

  public static final Duration DEFAULT_TIMEOUT_CHECK_DURATION = Duration.of(250, ChronoUnit.MILLIS);

  private final HeartbeatMonitor heartbeatMonitor;
  private final Duration timeoutCheckDuration;
  private final FeatureFlagClient featureFlagClient;
  private final UUID workspaceId;

  public HeartbeatTimeoutChaperone(final HeartbeatMonitor heartbeatMonitor,
                                   final Duration timeoutCheckDuration,
                                   final FeatureFlagClient featureFlagClient,
                                   final UUID workspaceId) {
    this.timeoutCheckDuration = timeoutCheckDuration;

    LOGGER.info("Starting source heartbeat check. Will check every {} minutes.", timeoutCheckDuration.toMinutes());

    this.heartbeatMonitor = heartbeatMonitor;
    this.featureFlagClient = featureFlagClient;
    this.workspaceId = workspaceId;
  }

  public Runnable runWithHeartbeatThread(final Runnable runnable, final ExecutorService executorService) {
    return () -> {
      final CompletableFuture<Void> runnableFuture = CompletableFuture.runAsync(runnable, executorService);
      final CompletableFuture<Void> heartbeatFuture = CompletableFuture.runAsync(this::monitor, executorService);

      try {
        CompletableFuture.anyOf(runnableFuture, heartbeatFuture).get();
      } catch (final InterruptedException e) {
        LOGGER.error("Heartbeat chaperone thread was interrupted.", e);
        return;
      } catch (final ExecutionException e) {
        // this should check explicitly for source and destination exceptions
        if (e.getCause() instanceof RuntimeException) {
          throw (RuntimeException) e.getCause();
        } else {
          throw new RuntimeException(e);
        }
      }

      LOGGER.info("thread status... heartbeat thread: {} , replication thread: {}", heartbeatFuture.isDone(), runnableFuture.isDone());

      boolean heartbeatTimedOut = false;
      if (heartbeatFuture.isDone() && !runnableFuture.isDone()) {
        heartbeatTimedOut = true;
        runnableFuture.cancel(true);
      }

      if (runnableFuture.isDone() && !heartbeatFuture.isDone()) {
        heartbeatFuture.cancel(true);
      }

      if (heartbeatTimedOut) {
        throw new HeartbeatTimeoutException(String.format("Heartbeat has stopped. Heartbeat freshness threshold: %s Actual heartbeat age: %s",
            heartbeatMonitor.getHeartbeatFreshnessThreshold(),
            heartbeatMonitor.getTimeSinceLastBeat().orElse(null)));
      }
    };
  }

  @SuppressWarnings("BusyWait")
  private void monitor() {
    while (true) {
      try {
        sleep(timeoutCheckDuration.toMillis());
      } catch (final InterruptedException e) {
        LOGGER.info("Heartbeat thread has been interrupted (this is expected; the heartbeat was healthy the whole time).");
        return;
      }

      // if not beating, return. otherwise, if it is beating or heartbeat hasn't started, continue.
      if (!heartbeatMonitor.isBeating().orElse(true)) {
        LOGGER.error("Source has stopped heart beating.");
        if (featureFlagClient.enabled(ShouldFailSyncIfHeartbeatFailure.INSTANCE, new Workspace(workspaceId))) {
          return;
        } else {
          LOGGER.info("Do not return because the feature flag is disable");
        }
      }
    }
  }

  public static class HeartbeatTimeoutException extends RuntimeException {

    private HeartbeatTimeoutException(final String message) {
      super(message);
    }

  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static java.lang.Thread.sleep;

import io.airbyte.workers.general.DefaultReplicationWorker.SourceException;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SourceHeartbeatMonitor {

  private static final Logger LOGGER = LoggerFactory.getLogger(SourceHeartbeatMonitor.class);

  private final HeartbeatMonitor heartbeatMonitor;
  private final int checkInterval;
  private final TimeUnit checkTimeUnit;

  public SourceHeartbeatMonitor() {
    this(new HeartbeatMonitor(DefaultAirbyteSource.HEARTBEAT_FRESH_DURATION), 5, TimeUnit.MINUTES);
  }

  public SourceHeartbeatMonitor(final HeartbeatMonitor heartbeatMonitor, final int checkInterval, final TimeUnit checkTimeUnit) {
    this.checkInterval = checkInterval;
    this.checkTimeUnit = checkTimeUnit;
    LOGGER.info("Starting source heartbeat check. Will check every {} {}.", checkInterval, checkTimeUnit);

    this.heartbeatMonitor = heartbeatMonitor;
  }

  public Runnable getMonitorThread() {
    return this::monitor;
  }

  public Runnable runWithHeartbeatThread(final Runnable runnable, final ExecutorService executorService, final AtomicBoolean cancelled) {
    return () -> {
      final CompletableFuture<Void> runnableToCancelIfTimeOut = CompletableFuture.runAsync(runnable, executorService);
      final CompletableFuture<Void> srcHeartbeatThread = CompletableFuture.runAsync(this::monitor, executorService);

      try {
        CompletableFuture.anyOf(runnableToCancelIfTimeOut, srcHeartbeatThread).get();
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      } catch (final ExecutionException e) {
        if(!cancelled.get()) {
          // this should check explicitly for source and destination exceptions
          if(e.getCause() instanceof RuntimeException) {
            throw (RuntimeException)e.getCause();
          } else {
            throw new RuntimeException(e);
          }
        }
      }

      LOGGER.info("thread status... heartbeat thread: {} , replication thread: {}", srcHeartbeatThread.isDone(), runnableToCancelIfTimeOut.isDone());

      boolean heartbeatTimedOut = false;
      if (srcHeartbeatThread.isDone() && !runnableToCancelIfTimeOut.isDone()) {
        heartbeatTimedOut = true;
        runnableToCancelIfTimeOut.cancel(true);
      }
      if (runnableToCancelIfTimeOut.isDone()) {
        srcHeartbeatThread.cancel(true);
      }

      if (heartbeatTimedOut) {
        throw new SourceException("source timed out");
      }

      // todo
      try {
        runnableToCancelIfTimeOut.get();
      } catch (final InterruptedException e) {
        e.printStackTrace();
      } catch (final ExecutionException e) {
        e.printStackTrace();
      }
    };
  }

  public void monitor() {
    while (true) {
      // todo handle
      try {
        sleep(checkTimeUnit.toMillis(checkInterval));
      } catch (final InterruptedException e) {
        LOGGER.info("Heartbeat thread has been interrupted (this is the expected way that it ends when the heartbeat never failed)");
      }
      if (!heartbeatMonitor.isBeating()) {
        LOGGER.info("source heartbeat has stopped");
        return;
      }
    }
  }

  public void beat() {
    heartbeatMonitor.beat();
  }

}

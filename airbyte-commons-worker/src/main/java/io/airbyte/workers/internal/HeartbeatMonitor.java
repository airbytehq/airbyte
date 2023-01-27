/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import com.google.common.annotations.VisibleForTesting;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;

/**
 * Tracks heartbeats and, when asked, says if it has been too long since the last heartbeat. He's
 * dead Jim!
 *
 * It is ThreadSafe.
 */
public class HeartbeatMonitor {

  public static final Duration DEFAULT_HEARTBEAT_FRESHNESS_THRESHOLD = Duration.of(5, ChronoUnit.MINUTES);

  private final Duration heartbeatFreshnessThreshold;
  private final Supplier<Instant> nowSupplier;
  private final AtomicReference<Instant> lastBeat;

  public HeartbeatMonitor(final Duration heartbeatFreshnessThreshold) {
    this(heartbeatFreshnessThreshold, Instant::now);
  }

  @VisibleForTesting
  public HeartbeatMonitor(final Duration heartbeatFreshnessThreshold, final Supplier<Instant> nowSupplier) {
    this.heartbeatFreshnessThreshold = heartbeatFreshnessThreshold;
    this.nowSupplier = nowSupplier;
    this.lastBeat = new AtomicReference<>(null);
  }

  /**
   * Register a heartbeat
   */
  public void beat() {
    lastBeat.set(nowSupplier.get());
  }

  /**
   *
   * @return true if the last heartbeat is still "fresh". i.e. time since last heartbeat is less than
   *         heartBeatFreshDuration. otherwise, false.
   */
  public Optional<Boolean> isBeating() {
    return getTimeSinceLastBeat().map(timeSinceLastBeat -> timeSinceLastBeat.compareTo(heartbeatFreshnessThreshold) < 0);
  }


  public Optional<Duration> getTimeSinceLastBeat() {
    final Instant instantFetched = lastBeat.get();

    if (instantFetched == null) {
      return Optional.empty();
    } else {
      return Optional.ofNullable(Duration.between(lastBeat.get(), nowSupplier.get()));
    }
  }
}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import com.google.common.annotations.VisibleForTesting;
import java.time.Duration;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;

/**
 * Tracks heartbeats and, when asked, says if it has been too long since the last heartbeat. He's
 * dead Jim!
 *
 * It is ThreadSafe.
 */
public class HeartbeatMonitor {

  private final Duration heartBeatFreshDuration;
  private final Supplier<Instant> nowSupplier;
  private final AtomicReference<Instant> lastBeat;

  public HeartbeatMonitor(final Duration heartBeatFreshDuration) {
    this(heartBeatFreshDuration, Instant::now);
  }

  @VisibleForTesting
  public HeartbeatMonitor(final Duration heartBeatFreshDuration, final Supplier<Instant> nowSupplier) {
    this.heartBeatFreshDuration = heartBeatFreshDuration;
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
  public boolean isBeating() {
    final Instant instantFetched = lastBeat.get();
    final Instant now = nowSupplier.get();
    return instantFetched != null && instantFetched.plus(heartBeatFreshDuration).isAfter(now);
  }

}

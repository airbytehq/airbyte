/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import com.google.common.annotations.VisibleForTesting;
import java.time.Duration;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;

public class HeartbeatMonitor {

  private final Duration heartBeatFreshDuration;
  private final Supplier<Instant> nowSupplier;
  private final AtomicReference<Instant> lastBeat;

  public HeartbeatMonitor(Duration heartBeatFreshDuration) {
    this(heartBeatFreshDuration, Instant::now);
  }

  @VisibleForTesting
  public HeartbeatMonitor(Duration heartBeatFreshDuration, Supplier<Instant> nowSupplier) {
    this.heartBeatFreshDuration = heartBeatFreshDuration;
    this.nowSupplier = nowSupplier;
    this.lastBeat = new AtomicReference<>(null);
  }

  public void beat() {
    lastBeat.set(nowSupplier.get());
  }

  public boolean isBeating() {
    final Instant instantFetched = lastBeat.get();
    final Instant now = nowSupplier.get();
    return instantFetched != null && instantFetched.plus(heartBeatFreshDuration).isAfter(now);
  }

}

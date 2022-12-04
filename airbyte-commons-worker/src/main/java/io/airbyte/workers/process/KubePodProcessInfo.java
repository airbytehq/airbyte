/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import java.lang.ProcessHandle.Info;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;

/**
 * Minimal Process info implementation to assist with debug logging.
 *
 * Current implement only logs out the Kubernetes pod corresponding to the JVM process.
 */
public class KubePodProcessInfo implements Info {

  private final String podName;

  public KubePodProcessInfo(final String podname) {
    this.podName = podname;
  }

  @Override
  public Optional<String> command() {
    return Optional.of(podName);
  }

  @Override
  public Optional<String> commandLine() {
    return Optional.of(podName);
  }

  @Override
  public Optional<String[]> arguments() {
    return Optional.empty();
  }

  @Override
  public Optional<Instant> startInstant() {
    return Optional.empty();
  }

  @Override
  public Optional<Duration> totalCpuDuration() {
    return Optional.empty();
  }

  @Override
  public Optional<String> user() {
    return Optional.empty();
  }

}

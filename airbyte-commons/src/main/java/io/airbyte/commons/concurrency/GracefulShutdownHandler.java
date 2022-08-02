/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.concurrency;

import java.time.Duration;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GracefulShutdownHandler extends Thread {

  private static final Logger LOGGER = LoggerFactory.getLogger(GracefulShutdownHandler.class);
  private final Duration terminateWaitDuration;
  private final ExecutorService[] threadPools;

  public GracefulShutdownHandler(final Duration terminateWaitDuration, final ExecutorService... threadPools) {
    this.terminateWaitDuration = terminateWaitDuration;
    this.threadPools = threadPools.clone();
  }

  @Override
  public void run() {
    for (final ExecutorService threadPool : threadPools) {
      threadPool.shutdown();

      try {
        if (!threadPool.awaitTermination(terminateWaitDuration.getSeconds(), TimeUnit.SECONDS)) {
          LOGGER.error("Unable to kill threads by shutdown timeout.");
        }
      } catch (final InterruptedException e) {
        LOGGER.error("Wait for graceful thread shutdown interrupted.", e);
      }
    }
  }

}

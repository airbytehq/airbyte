/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.workers.process.KubePodProcess;
import io.micronaut.context.ApplicationContext;
import io.micronaut.runtime.event.ApplicationStartupEvent;
import io.micronaut.runtime.exceptions.ApplicationStartupException;
import jakarta.inject.Singleton;
import java.lang.invoke.MethodHandles;
import java.nio.file.Path;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
class EventListeners {

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

  private static final Duration MAX_WAIT_FOR_FILE_COPY = Duration.ofSeconds(60);

  private final ApplicationContext ctx;

  EventListeners(final ApplicationContext ctx) {
    this.ctx = ctx;
  }

  // @EventListener
  public void start(final ApplicationStartupEvent event) {
    final var file = Path.of(KubePodProcess.CONFIG_DIR, KubePodProcess.SUCCESS_FILE_NAME).toFile();
    var secondsWaited = 0;
    while (!file.exists() && secondsWaited < MAX_WAIT_FOR_FILE_COPY.toSeconds()) {
      log.info("Waiting for config file transfers to complete...");
      try {
        Thread.sleep(1000);
      } catch (final InterruptedException e) {
        throw new ApplicationStartupException("sleeping interrupted");
      }
      secondsWaited++;
    }

    if (!file.exists()) {
      log.error("Config files did not transfer within the maximum amount of time ({} seconds)!",
          MAX_WAIT_FOR_FILE_COPY.toSeconds());
      throw new ApplicationStartupException("missing config file");
    }
  }
}

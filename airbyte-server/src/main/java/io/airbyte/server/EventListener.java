/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.micronaut.runtime.event.ApplicationStartupEvent;
import jakarta.inject.Inject;
import jakarta.inject.Singleton;
import java.util.concurrent.Executors;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class EventListener {

  @Inject
  ServerRunnable serverRunnable;

  @io.micronaut.runtime.event.annotation.EventListener
  public void startEmitters(final ApplicationStartupEvent event) {
    try {
      log.error("Starting server");

      Executors.newFixedThreadPool(1).submit(() -> {
        try {
          serverRunnable.start();
        } catch (final Exception e) {
          throw new RuntimeException(e);
        }
      });
      // serverRunnable.start();

      log.error("Server Started");
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.micronaut.runtime.event.ApplicationStartupEvent;
import io.micronaut.scheduling.TaskExecutors;
import io.micronaut.scheduling.annotation.ExecuteOn;
import jakarta.inject.Inject;
import jakarta.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class EventListener {

  @Inject
  ServerRunnable serverRunnable;

  @io.micronaut.runtime.event.annotation.EventListener
  @ExecuteOn(TaskExecutors.IO)
  public void startEmitters(final ApplicationStartupEvent event) {
    try {
      log.error("Starting server");

      serverRunnable.start();
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

}

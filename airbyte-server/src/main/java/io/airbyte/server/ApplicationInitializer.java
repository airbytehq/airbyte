/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.discovery.event.ServiceReadyEvent;
import jakarta.inject.Inject;
import jakarta.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class ApplicationInitializer implements ApplicationEventListener<ServiceReadyEvent> {

  @Inject
  ServerRunnable serverRunnable;

  @Override
  public void onApplicationEvent(final ServiceReadyEvent event) {
    try {
      log.error("Starting server");
      serverRunnable.start();
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

}

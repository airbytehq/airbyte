/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.discovery.event.ServiceReadyEvent;
import jakarta.inject.Inject;

public class ApplicationInitializer implements ApplicationEventListener<ServiceReadyEvent> {

  @Inject
  ServerRunnable serverRunnable;

  @Override
  public void onApplicationEvent(final ServiceReadyEvent event) {
    try {
      serverRunnable.start();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

}

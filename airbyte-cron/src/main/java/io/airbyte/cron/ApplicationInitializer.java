/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron;

import io.airbyte.commons.temporal.TemporalInitializationUtils;
import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.discovery.event.ServiceReadyEvent;
import jakarta.inject.Inject;

public class ApplicationInitializer implements ApplicationEventListener<ServiceReadyEvent> {

  @Inject
  private TemporalInitializationUtils temporalInitializationUtils;

  @Override
  public void onApplicationEvent(ServiceReadyEvent event) {
    temporalInitializationUtils.waitForTemporalNamespace();
  }

}

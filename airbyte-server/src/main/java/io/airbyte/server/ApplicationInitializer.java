package io.airbyte.server;

import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.discovery.event.ServiceReadyEvent;

public class ApplicationInitializer implements ApplicationEventListener<ServiceReadyEvent> {

  @Override public void onApplicationEvent(final ServiceReadyEvent event) {

  }
}

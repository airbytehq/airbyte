/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.micronaut.context.ApplicationContext;
import io.micronaut.runtime.event.ApplicationStartupEvent;
import io.micronaut.runtime.event.annotation.EventListener;
import jakarta.inject.Singleton;
import java.lang.invoke.MethodHandles;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
class EventListeners {

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

  private final ApplicationContext ctx;

  EventListeners(final ApplicationContext ctx) {
    this.ctx = ctx;
  }

  @EventListener
  public void start(final ApplicationStartupEvent event) {
    throw new RuntimeException("abc");
    // log.info("stopping!!!");
    // ctx.stop();
  }

}

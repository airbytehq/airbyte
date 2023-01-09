/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.micronaut.runtime.event.ApplicationShutdownEvent;
import io.micronaut.runtime.event.ApplicationStartupEvent;
import io.micronaut.runtime.event.annotation.EventListener;
import jakarta.inject.Singleton;
import java.lang.invoke.MethodHandles;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * EventListeners registers event listeners for the startup and shutdown events from Micronaut.
 */
@Singleton
class EventListeners {

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());
  private final List<Emitter> emitters;
  private final ScheduledExecutorService executor;

  EventListeners(final List<Emitter> emitters) {
    this.emitters = emitters;
    this.executor = Executors.newScheduledThreadPool(emitters.size());
  }

  /**
   * Manually registers all the emitters to run on startup.
   *
   * @param event unused but required in order to listen to the startup event.
   */
  @EventListener
  public void startEmitters(final ApplicationStartupEvent event) {
    emitters.forEach(emitter -> executor.scheduleAtFixedRate(emitter::Emit, 0, emitter.getDuration().getSeconds(), TimeUnit.SECONDS));
    log.info("registered {} emitters", emitters.size());
  }

  /**
   * Attempts to cleanly shutdown the running emitters
   *
   * @param event unused but required in order to listen to the shutdown event.
   */
  @EventListener
  public void stopEmitters(final ApplicationShutdownEvent event) {
    log.info("shutting down emitters");
    executor.shutdown();
  }

}

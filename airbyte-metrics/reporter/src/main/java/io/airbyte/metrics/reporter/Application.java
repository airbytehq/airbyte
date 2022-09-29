/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.runtime.Micronaut;
import io.micronaut.runtime.server.event.ServerStartupEvent;
import jakarta.inject.Singleton;
import java.lang.invoke.MethodHandles;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Metric Reporter application.
 * <p>
 * Responsible for emitting metric information on a periodic basis.
 */
@Singleton
public class Application implements ApplicationEventListener<ServerStartupEvent> {

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());
  private final Emitter[] emitters;

  public Application(final Emitter[] emitters) {
    this.emitters = emitters;
  }

  public static void main(final String[] args) {
    Micronaut.run(Application.class, args);
  }

  /**
   * Manually registers all the emitters to run.
   *
   * @param event the event to respond to, not utilized but required per the method signature
   *              <p>
   *              See https://guides.micronaut.io/latest/micronaut-scheduled-gradle-java.html for documentation.
   */
  @Override
  public void onApplicationEvent(final ServerStartupEvent event) {
    final var pollers = Executors.newScheduledThreadPool(emitters.length);
    for (final var emitter : emitters) {
      pollers.scheduleAtFixedRate(emitter::Emit, 0, emitter.getDuration().getSeconds(), TimeUnit.SECONDS);
    }
    log.info("registered {} emitters", emitters.length);
  }
}

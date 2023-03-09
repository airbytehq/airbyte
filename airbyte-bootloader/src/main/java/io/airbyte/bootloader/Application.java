/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import io.micronaut.context.ApplicationContext;
import io.micronaut.runtime.Micronaut;
import lombok.extern.slf4j.Slf4j;

/**
 * Main application entry point responsible for starting the server and invoking the bootstrapping
 * of the Airbyte environment.
 */
@Slf4j
public class Application {

  public static void main(final String[] args) {
    try {
      final ApplicationContext applicationContext = Micronaut.run(Application.class, args);
      final Bootloader bootloader = applicationContext.getBean(Bootloader.class);
      bootloader.load();
      System.exit(0);
    } catch (final Exception e) {
      log.error("Unable to bootstrap Airbyte environment.", e);
      System.exit(-1);
    }
  }

}

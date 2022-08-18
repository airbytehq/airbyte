/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron;

import io.airbyte.cron.selfhealing.Temporal;
import io.micronaut.runtime.Micronaut;
import javax.inject.Inject;

/**
 * Micronaut server responsible of running scheduled method. The methods need to be separated in
 * Bean based on what they are cleaning and contain a method annotated with `@Scheduled`
 *
 * Injected object looks unused but they are not
 */
public class MicronautCronRunner {

  @Inject
  Temporal temporal;

  public static void main(final String[] args) {
    Micronaut.run(MicronautCronRunner.class);
  }

}

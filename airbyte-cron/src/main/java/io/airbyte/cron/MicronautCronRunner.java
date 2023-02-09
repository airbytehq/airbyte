/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron;

import io.micronaut.runtime.Micronaut;

/**
 * Micronaut server responsible of running scheduled method. The methods need to be separated in
 * Bean based on what they are cleaning and contain a method annotated with `@Scheduled`
 *
 * Injected object looks unused but they are not
 */
public class MicronautCronRunner {

  public static final String SCHEDULED_TRACE_OPERATION_NAME = "scheduled";

  public static void main(final String[] args) {
    Micronaut.build(args)
        .mainClass(MicronautCronRunner.class)
        .start();
  }

}

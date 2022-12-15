/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.config;

import io.airbyte.config.Configs.WorkerEnvironment;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.env.Environment;
import jakarta.inject.Singleton;

@Factory
public class CommonFactory {

  @Singleton
  public WorkerEnvironment workerEnvironment(final Environment environment) {
    return environment.getActiveNames().contains(Environment.KUBERNETES) ? WorkerEnvironment.KUBERNETES : WorkerEnvironment.DOCKER;
  }

}

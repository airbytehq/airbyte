/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.config;

import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.server.handlers.AttemptHandler;
import io.airbyte.server.handlers.HealthCheckHandler;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Singleton;

@Factory
public class HandlerFactory {

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  public HealthCheckHandler configRepository(final ConfigRepository configRepository) {
    return new HealthCheckHandler(configRepository);
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  public AttemptHandler attemptHandler(final JobPersistence jobPersistence) {
    return new AttemptHandler(jobPersistence);
  }

}

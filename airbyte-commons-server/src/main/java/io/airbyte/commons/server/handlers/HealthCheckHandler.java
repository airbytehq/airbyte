/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import io.airbyte.api.model.generated.HealthCheckRead;
import io.airbyte.config.persistence.ConfigRepository;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

@Singleton
public class HealthCheckHandler {

  private final ConfigRepository repository;

  public HealthCheckHandler(@Named("configRepository") final ConfigRepository repository) {
    this.repository = repository;
  }

  public HealthCheckRead health() {
    return new HealthCheckRead().available(repository.healthCheck());
  }

}

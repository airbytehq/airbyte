/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.HealthCheckRead;
import io.airbyte.config.persistence.ConfigRepository;

public class HealthCheckHandler {

  private final ConfigRepository repository;

  public HealthCheckHandler(ConfigRepository repository) {
    this.repository = repository;
  }

  public HealthCheckRead health() {
    return new HealthCheckRead().available(repository.healthCheck());
  }

}

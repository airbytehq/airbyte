/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.generated.HealthCheckRead;
import io.airbyte.config.persistence.ConfigRepository;

public class HealthCheckHandler {

  private final ConfigRepository repository;

  public HealthCheckHandler(final ConfigRepository repository) {
    this.repository = repository;
  }

  public HealthCheckRead health() {
    return new HealthCheckRead().available(repository.healthCheck());
  }

}

/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.HealthCheckRead;
import io.airbyte.config.persistence.ConfigRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HealthCheckHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(HealthCheckHandler.class);

  private final ConfigRepository configRepository;

  public HealthCheckHandler(ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  // todo (cgardens) - add more checks as we go.
  public HealthCheckRead health() {
    boolean databaseHealth = false;
    try {
      configRepository.listStandardWorkspaces(true);
      databaseHealth = true;
    } catch (Exception e) {
      LOGGER.error("database health check failed.");
    }

    return new HealthCheckRead().db(databaseHealth);
  }

}

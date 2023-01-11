/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.HealthApi;
import io.airbyte.api.model.generated.HealthCheckRead;
import io.airbyte.server.handlers.HealthCheckHandler;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;

@Controller("/api/v1/health")
public class HealthApiController implements HealthApi {

  private final HealthCheckHandler healthCheckHandler;

  public HealthApiController(final HealthCheckHandler healthCheckHandler) {
    this.healthCheckHandler = healthCheckHandler;
  }

  @Override
  @Get(produces = MediaType.APPLICATION_JSON)
  public HealthCheckRead getHealthCheck() {
    return healthCheckHandler.health();
  }

}

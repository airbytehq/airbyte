/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.generated.HealthCheckRead;
import io.airbyte.server.handlers.HealthCheckHandler;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiResponse;
import io.swagger.annotations.ApiResponses;

@Controller("/api/v1/health")
public class HealthApiController {

  private final HealthCheckHandler healthCheckHandler;

  public HealthApiController(final HealthCheckHandler healthCheckHandler) {
    this.healthCheckHandler = healthCheckHandler;
  }

  @Get(produces = MediaType.APPLICATION_JSON)
  @ApiOperation(value = "Health Check",
                notes = "",
                tags = {"health"})
  @ApiResponses(value = {
    @ApiResponse(code = 200,
                 message = "Successful operation",
                 response = HealthCheckRead.class)})
  public HealthCheckRead getHealthCheck() {
    return healthCheckHandler.health();
  }

}

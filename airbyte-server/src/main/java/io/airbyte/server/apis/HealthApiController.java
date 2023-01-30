/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.HealthApi;
import io.airbyte.api.model.generated.HealthCheckRead;
import io.airbyte.commons.server.handlers.HealthCheckHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/health")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Secured(SecurityRule.IS_ANONYMOUS)
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

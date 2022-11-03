/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.HealthApi;
import io.airbyte.api.model.generated.HealthCheckRead;
import io.airbyte.server.handlers.HealthCheckHandler;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/health")
@AllArgsConstructor
public class HealthApiController implements HealthApi {

  private final HealthCheckHandler healthCheckHandler;

  @Override
  public HealthCheckRead getHealthCheck() {
    return healthCheckHandler.health();
  }

}

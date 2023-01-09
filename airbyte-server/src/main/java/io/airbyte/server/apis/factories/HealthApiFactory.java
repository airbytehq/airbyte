/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.HealthApiController;
import io.airbyte.server.handlers.HealthCheckHandler;
import org.glassfish.hk2.api.Factory;

public class HealthApiFactory implements Factory<HealthApiController> {

  private static HealthCheckHandler healthCheckHandler;

  public static void setValues(final HealthCheckHandler healthCheckHandler) {
    HealthApiFactory.healthCheckHandler = healthCheckHandler;
  }

  @Override
  public HealthApiController provide() {
    return new HealthApiController(healthCheckHandler);
  }

  @Override
  public void dispose(final HealthApiController instance) {
    /* no op */
  }

}

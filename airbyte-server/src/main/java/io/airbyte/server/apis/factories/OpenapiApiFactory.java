/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.OpenapiApiController;
import io.airbyte.server.handlers.OpenApiConfigHandler;
import org.glassfish.hk2.api.Factory;

public class OpenapiApiFactory implements Factory<OpenapiApiController> {

  private static OpenApiConfigHandler openApiConfigHandler;

  public static void setValues(final OpenApiConfigHandler openApiConfigHandler) {
    OpenapiApiFactory.openApiConfigHandler = openApiConfigHandler;
  }

  @Override
  public OpenapiApiController provide() {
    return new OpenapiApiController(openApiConfigHandler);
  }

  @Override
  public void dispose(final OpenapiApiController instance) {
    /* no op */
  }

}

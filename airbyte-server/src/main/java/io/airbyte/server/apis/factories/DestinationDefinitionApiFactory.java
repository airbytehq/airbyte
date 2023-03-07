/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.DestinationDefinitionApiController;
import io.airbyte.server.handlers.DestinationDefinitionsHandler;
import org.glassfish.hk2.api.Factory;

public class DestinationDefinitionApiFactory implements Factory<DestinationDefinitionApiController> {

  private static DestinationDefinitionsHandler destinationDefinitionsHandler;

  public static void setValues(final DestinationDefinitionsHandler destinationDefinitionsHandler) {
    DestinationDefinitionApiFactory.destinationDefinitionsHandler = destinationDefinitionsHandler;
  }

  @Override
  public DestinationDefinitionApiController provide() {
    return new DestinationDefinitionApiController(destinationDefinitionsHandler);
  }

  @Override
  public void dispose(final DestinationDefinitionApiController instance) {
    /* no op */
  }

}

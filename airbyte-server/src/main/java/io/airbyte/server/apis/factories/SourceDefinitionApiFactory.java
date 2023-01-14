/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.SourceDefinitionApiController;
import io.airbyte.server.handlers.SourceDefinitionsHandler;
import org.glassfish.hk2.api.Factory;

public class SourceDefinitionApiFactory implements Factory<SourceDefinitionApiController> {

  private static SourceDefinitionsHandler sourceDefinitionsHandler;

  public static void setValues(final SourceDefinitionsHandler sourceDefinitionsHandler) {
    SourceDefinitionApiFactory.sourceDefinitionsHandler = sourceDefinitionsHandler;
  }

  @Override
  public SourceDefinitionApiController provide() {
    return new SourceDefinitionApiController(SourceDefinitionApiFactory.sourceDefinitionsHandler);
  }

  @Override
  public void dispose(final SourceDefinitionApiController instance) {
    /* no op */
  }

}

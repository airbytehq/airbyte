/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.SourceDefinitionApiController;
import io.airbyte.server.apis.factories.SourceDefinitionApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class SourceDefinitionApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(SourceDefinitionApiFactory.class)
        .to(SourceDefinitionApiController.class)
        .in(RequestScoped.class);
  }

}

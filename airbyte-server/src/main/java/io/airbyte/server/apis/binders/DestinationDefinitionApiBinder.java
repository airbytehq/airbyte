/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.DestinationDefinitionApiController;
import io.airbyte.server.apis.factories.DestinationDefinitionApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class DestinationDefinitionApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(DestinationDefinitionApiFactory.class)
        .to(DestinationDefinitionApiController.class)
        .in(RequestScoped.class);
  }

}

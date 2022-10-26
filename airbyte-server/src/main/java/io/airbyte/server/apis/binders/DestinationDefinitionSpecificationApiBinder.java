/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.DestinationDefinitionSpecificationApiController;
import io.airbyte.server.apis.factories.DestinationDefinitionSpecificationApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class DestinationDefinitionSpecificationApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(DestinationDefinitionSpecificationApiFactory.class)
        .to(DestinationDefinitionSpecificationApiController.class)
        .in(RequestScoped.class);
  }

}

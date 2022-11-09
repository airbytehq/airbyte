/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.SourceDefinitionSpecificationApiController;
import io.airbyte.server.apis.factories.SourceDefinitionSpecificationApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class SourceDefinitionSpecificationApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(SourceDefinitionSpecificationApiFactory.class)
        .to(SourceDefinitionSpecificationApiController.class)
        .in(RequestScoped.class);
  }

}

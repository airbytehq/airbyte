/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.OpenapiApiController;
import io.airbyte.server.apis.factories.OpenapiApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class OpenapiApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(OpenapiApiFactory.class)
        .to(OpenapiApiController.class)
        .in(RequestScoped.class);
  }

}

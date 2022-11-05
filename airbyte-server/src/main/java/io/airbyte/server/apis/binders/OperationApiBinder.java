/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.OperationApiController;
import io.airbyte.server.apis.factories.OperationApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class OperationApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(OperationApiFactory.class)
        .to(OperationApiController.class)
        .in(RequestScoped.class);
  }

}

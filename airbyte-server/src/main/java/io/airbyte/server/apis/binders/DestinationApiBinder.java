/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.DestinationApiController;
import io.airbyte.server.apis.factories.DestinationApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class DestinationApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(DestinationApiFactory.class)
        .to(DestinationApiController.class)
        .in(RequestScoped.class);
  }

}

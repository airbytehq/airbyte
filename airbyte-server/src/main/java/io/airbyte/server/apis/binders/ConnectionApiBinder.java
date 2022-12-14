/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.ConnectionApiController;
import io.airbyte.server.apis.factories.ConnectionApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class ConnectionApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(ConnectionApiFactory.class)
        .to(ConnectionApiController.class)
        .in(RequestScoped.class);
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.StateApiController;
import io.airbyte.server.apis.factories.StateApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class StateApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(StateApiFactory.class)
        .to(StateApiController.class)
        .in(RequestScoped.class);
  }

}

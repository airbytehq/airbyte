/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.AttemptApiController;
import io.airbyte.server.apis.factories.AttemptApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class AttemptApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(AttemptApiFactory.class)
        .to(AttemptApiController.class)
        .in(RequestScoped.class);
  }

}

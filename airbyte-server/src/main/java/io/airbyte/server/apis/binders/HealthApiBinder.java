/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.HealthApiController;
import io.airbyte.server.apis.factories.HealthApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class HealthApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(HealthApiFactory.class)
        .to(HealthApiController.class)
        .in(RequestScoped.class);
  }

}

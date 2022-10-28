/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.LogsApiController;
import io.airbyte.server.apis.factories.LogsApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class LogsApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(LogsApiFactory.class)
        .to(LogsApiController.class)
        .in(RequestScoped.class);
  }

}

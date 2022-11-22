/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.WebBackendApiController;
import io.airbyte.server.apis.factories.WebBackendApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class WebBackendApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(WebBackendApiFactory.class)
        .to(WebBackendApiController.class)
        .in(RequestScoped.class);
  }

}

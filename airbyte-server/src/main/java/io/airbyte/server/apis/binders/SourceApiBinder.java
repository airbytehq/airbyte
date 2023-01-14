/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.SourceApiController;
import io.airbyte.server.apis.factories.SourceApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class SourceApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(SourceApiFactory.class)
        .to(SourceApiController.class)
        .in(RequestScoped.class);
  }

}

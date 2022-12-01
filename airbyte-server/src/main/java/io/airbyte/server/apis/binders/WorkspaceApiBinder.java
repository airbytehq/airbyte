/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.WorkspaceApiController;
import io.airbyte.server.apis.factories.WorkspaceApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class WorkspaceApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(WorkspaceApiFactory.class)
        .to(WorkspaceApiController.class)
        .in(RequestScoped.class);
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.JobsApiController;
import io.airbyte.server.apis.factories.JobsApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class JobsApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(JobsApiFactory.class)
        .to(JobsApiController.class)
        .in(RequestScoped.class);
  }

}

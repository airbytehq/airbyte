/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.SchedulerApiController;
import io.airbyte.server.apis.factories.SchedulerApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class SchedulerApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(SchedulerApiFactory.class)
        .to(SchedulerApiController.class)
        .in(RequestScoped.class);
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.DestinationDefinitionSpecificationApiController;
import io.airbyte.server.handlers.SchedulerHandler;
import org.glassfish.hk2.api.Factory;

public class DestinationDefinitionSpecificationApiFactory implements Factory<DestinationDefinitionSpecificationApiController> {

  private static SchedulerHandler schedulerHandler;

  public static void setValues(final SchedulerHandler schedulerHandler) {
    DestinationDefinitionSpecificationApiFactory.schedulerHandler = schedulerHandler;
  }

  @Override
  public DestinationDefinitionSpecificationApiController provide() {
    return new DestinationDefinitionSpecificationApiController(DestinationDefinitionSpecificationApiFactory.schedulerHandler);
  }

  @Override
  public void dispose(final DestinationDefinitionSpecificationApiController instance) {

  }

}

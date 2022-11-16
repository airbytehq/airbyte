/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.SourceDefinitionSpecificationApiController;
import io.airbyte.server.handlers.SchedulerHandler;
import org.glassfish.hk2.api.Factory;

public class SourceDefinitionSpecificationApiFactory implements Factory<SourceDefinitionSpecificationApiController> {

  private static SchedulerHandler schedulerHandler;

  public static void setValues(final SchedulerHandler schedulerHandler) {
    SourceDefinitionSpecificationApiFactory.schedulerHandler = schedulerHandler;
  }

  @Override
  public SourceDefinitionSpecificationApiController provide() {
    return new SourceDefinitionSpecificationApiController(SourceDefinitionSpecificationApiFactory.schedulerHandler);
  }

  @Override
  public void dispose(final SourceDefinitionSpecificationApiController instance) {
    /* no op */
  }

}

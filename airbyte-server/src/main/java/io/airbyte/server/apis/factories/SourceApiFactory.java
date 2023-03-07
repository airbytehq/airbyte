/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.SourceApiController;
import io.airbyte.server.handlers.SchedulerHandler;
import io.airbyte.server.handlers.SourceHandler;
import org.glassfish.hk2.api.Factory;

public class SourceApiFactory implements Factory<SourceApiController> {

  private static SchedulerHandler schedulerHandler;
  private static SourceHandler sourceHandler;

  public static void setValues(final SchedulerHandler schedulerHandler, final SourceHandler sourceHandler) {
    SourceApiFactory.schedulerHandler = schedulerHandler;
    SourceApiFactory.sourceHandler = sourceHandler;
  }

  @Override
  public SourceApiController provide() {
    return new SourceApiController(schedulerHandler, sourceHandler);
  }

  @Override
  public void dispose(final SourceApiController instance) {
    /* no op */
  }

}

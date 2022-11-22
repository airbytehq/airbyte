/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.SchedulerApiController;
import io.airbyte.server.handlers.SchedulerHandler;
import org.glassfish.hk2.api.Factory;

public class SchedulerApiFactory implements Factory<SchedulerApiController> {

  private static SchedulerHandler schedulerHandler;

  public static void setValues(final SchedulerHandler schedulerHandler) {
    SchedulerApiFactory.schedulerHandler = schedulerHandler;
  }

  @Override
  public SchedulerApiController provide() {
    return new SchedulerApiController(SchedulerApiFactory.schedulerHandler);
  }

  @Override
  public void dispose(final SchedulerApiController instance) {
    /* no op */
  }

}

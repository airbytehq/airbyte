/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.JobsApiController;
import io.airbyte.server.handlers.JobHistoryHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import org.glassfish.hk2.api.Factory;

public class JobsApiFactory implements Factory<JobsApiController> {

  private static JobHistoryHandler jobHistoryHandler;
  private static SchedulerHandler schedulerHandler;

  public static void setValues(final JobHistoryHandler jobHistoryHandler, final SchedulerHandler schedulerHandler) {
    JobsApiFactory.jobHistoryHandler = jobHistoryHandler;
    JobsApiFactory.schedulerHandler = schedulerHandler;
  }

  @Override
  public JobsApiController provide() {
    return new JobsApiController(jobHistoryHandler, schedulerHandler);
  }

  @Override
  public void dispose(final JobsApiController instance) {
    /* no op */
  }

}

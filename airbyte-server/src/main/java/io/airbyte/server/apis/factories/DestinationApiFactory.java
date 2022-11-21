/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.DestinationApiController;
import io.airbyte.server.handlers.DestinationHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import java.util.Map;
import org.glassfish.hk2.api.Factory;
import org.slf4j.MDC;

public class DestinationApiFactory implements Factory<DestinationApiController> {

  private static DestinationHandler destinationHandler;
  private static SchedulerHandler schedulerHandler;
  private static Map<String, String> mdc;

  public static void setValues(final DestinationHandler destinationHandler,
                               final SchedulerHandler schedulerHandler,
                               final Map<String, String> mdc) {
    DestinationApiFactory.destinationHandler = destinationHandler;
    DestinationApiFactory.schedulerHandler = schedulerHandler;
    DestinationApiFactory.mdc = mdc;
  }

  @Override
  public DestinationApiController provide() {
    MDC.setContextMap(DestinationApiFactory.mdc);

    return new DestinationApiController(destinationHandler, schedulerHandler);
  }

  @Override
  public void dispose(final DestinationApiController instance) {
    /* no op */
  }

}

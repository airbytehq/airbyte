/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.ConnectionApiController;
import io.airbyte.server.handlers.ConnectionsHandler;
import io.airbyte.server.handlers.OperationsHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import java.util.Map;
import org.glassfish.hk2.api.Factory;
import org.slf4j.MDC;

public class ConnectionApiFactory implements Factory<ConnectionApiController> {

  private static ConnectionsHandler connectionsHandler;
  private static OperationsHandler operationsHandler;
  private static SchedulerHandler schedulerHandler;
  private static Map<String, String> mdc;

  public static void setValues(final ConnectionsHandler connectionsHandler,
                               final OperationsHandler operationsHandler,
                               final SchedulerHandler schedulerHandler,
                               final Map<String, String> mdc) {
    ConnectionApiFactory.connectionsHandler = connectionsHandler;
    ConnectionApiFactory.operationsHandler = operationsHandler;
    ConnectionApiFactory.schedulerHandler = schedulerHandler;
    ConnectionApiFactory.mdc = mdc;
  }

  @Override
  public ConnectionApiController provide() {
    MDC.setContextMap(ConnectionApiFactory.mdc);

    return new ConnectionApiController(connectionsHandler, operationsHandler, schedulerHandler);
  }

  @Override
  public void dispose(final ConnectionApiController instance) {
    /* no op */
  }

}

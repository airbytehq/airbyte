/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.LogsApiController;
import io.airbyte.server.handlers.LogsHandler;
import org.glassfish.hk2.api.Factory;

public class LogsApiFactory implements Factory<LogsApiController> {

  private static LogsHandler logsHandler;

  public static void setValues(final LogsHandler logsHandler) {
    LogsApiFactory.logsHandler = logsHandler;
  }

  @Override
  public LogsApiController provide() {
    return new LogsApiController(logsHandler);
  }

  @Override
  public void dispose(final LogsApiController instance) {
    /* no op */
  }

}

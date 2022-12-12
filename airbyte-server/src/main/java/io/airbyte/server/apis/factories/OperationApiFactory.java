/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.OperationApiController;
import io.airbyte.server.handlers.OperationsHandler;
import org.glassfish.hk2.api.Factory;

public class OperationApiFactory implements Factory<OperationApiController> {

  private static OperationsHandler operationsHandler;

  public static void setValues(final OperationsHandler operationsHandler) {
    OperationApiFactory.operationsHandler = operationsHandler;
  }

  @Override
  public OperationApiController provide() {
    return new OperationApiController(OperationApiFactory.operationsHandler);
  }

  @Override
  public void dispose(final OperationApiController instance) {
    /* no op */
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.AttemptApiController;
import io.airbyte.server.handlers.AttemptHandler;
import java.util.Map;
import org.glassfish.hk2.api.Factory;
import org.slf4j.MDC;

public class AttemptApiFactory implements Factory<AttemptApiController> {

  private static AttemptHandler attemptHandler;
  private static Map<String, String> mdc;

  public static void setValues(final AttemptHandler attemptHandler, final Map<String, String> mdc) {
    AttemptApiFactory.attemptHandler = attemptHandler;
    AttemptApiFactory.mdc = mdc;
  }

  @Override
  public AttemptApiController provide() {
    MDC.setContextMap(AttemptApiFactory.mdc);

    return new AttemptApiController(attemptHandler);
  }

  @Override
  public void dispose(final AttemptApiController instance) {
    /* no op */
  }

}

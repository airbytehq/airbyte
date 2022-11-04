/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.WebBackendApiController;
import io.airbyte.server.handlers.WebBackendConnectionsHandler;
import io.airbyte.server.handlers.WebBackendGeographiesHandler;
import org.glassfish.hk2.api.Factory;

public class WebBackendApiFactory implements Factory<WebBackendApiController> {

  private static WebBackendConnectionsHandler webBackendConnectionsHandler;
  private static WebBackendGeographiesHandler webBackendGeographiesHandler;

  public static void setValues(final WebBackendConnectionsHandler webBackendConnectionsHandler,
                               final WebBackendGeographiesHandler webBackendGeographiesHandler) {
    WebBackendApiFactory.webBackendConnectionsHandler = webBackendConnectionsHandler;
    WebBackendApiFactory.webBackendGeographiesHandler = webBackendGeographiesHandler;
  }

  @Override
  public WebBackendApiController provide() {
    return new WebBackendApiController(WebBackendApiFactory.webBackendConnectionsHandler, WebBackendApiFactory.webBackendGeographiesHandler);
  }

  @Override
  public void dispose(final WebBackendApiController instance) {
    /* no op */
  }

}

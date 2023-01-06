/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.DestinationOauthApiController;
import io.airbyte.server.handlers.OAuthHandler;
import org.glassfish.hk2.api.Factory;

public class DestinationOauthApiFactory implements Factory<DestinationOauthApiController> {

  private static OAuthHandler oAuthHandler;

  public static void setValues(final OAuthHandler oAuthHandler) {
    DestinationOauthApiFactory.oAuthHandler = oAuthHandler;
  }

  @Override
  public DestinationOauthApiController provide() {
    return new DestinationOauthApiController(oAuthHandler);
  }

  @Override
  public void dispose(final DestinationOauthApiController instance) {
    /* no op */
  }

}

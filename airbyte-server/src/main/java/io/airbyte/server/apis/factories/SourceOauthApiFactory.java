/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.SourceOauthApiController;
import io.airbyte.server.handlers.OAuthHandler;
import org.glassfish.hk2.api.Factory;

public class SourceOauthApiFactory implements Factory<SourceOauthApiController> {

  private static OAuthHandler oAuthHandler;

  public static void setValues(final OAuthHandler oAuthHandler) {
    SourceOauthApiFactory.oAuthHandler = oAuthHandler;
  }

  @Override
  public SourceOauthApiController provide() {
    return new SourceOauthApiController(SourceOauthApiFactory.oAuthHandler);
  }

  @Override
  public void dispose(final SourceOauthApiController instance) {
    /* no op */
  }

}

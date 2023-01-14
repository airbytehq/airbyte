/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.SourceOauthApiController;
import io.airbyte.server.apis.factories.SourceOauthApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class SourceOauthApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(SourceOauthApiFactory.class)
        .to(SourceOauthApiController.class)
        .in(RequestScoped.class);
  }

}

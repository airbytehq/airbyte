/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.DestinationOauthApiController;
import io.airbyte.server.apis.factories.DestinationOauthApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class DestinationOauthApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(DestinationOauthApiFactory.class)
        .to(DestinationOauthApiController.class)
        .in(RequestScoped.class);
  }

}

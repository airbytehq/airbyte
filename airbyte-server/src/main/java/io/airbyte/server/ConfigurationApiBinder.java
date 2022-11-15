/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.server.apis.ConfigurationApi;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class ConfigurationApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(ConfigurationApiFactory.class)
        .to(ConfigurationApi.class)
        .in(RequestScoped.class);
  }

}

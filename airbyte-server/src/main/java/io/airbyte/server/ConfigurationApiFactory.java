/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.server.apis.ConfigurationApi;
import java.util.Map;
import org.glassfish.hk2.api.Factory;
import org.slf4j.MDC;

public class ConfigurationApiFactory implements Factory<ConfigurationApi> {

  private static Map<String, String> mdc;

  public static void setValues(
                               final Map<String, String> mdc) {
    ConfigurationApiFactory.mdc = mdc;
  }

  @Override
  public ConfigurationApi provide() {
    MDC.setContextMap(ConfigurationApiFactory.mdc);

    return new ConfigurationApi();
  }

  @Override
  public void dispose(final ConfigurationApi service) {
    /* noop */
  }

}

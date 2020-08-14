package io.dataline.server;

import io.dataline.server.apis.ConfigurationApi;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.HttpHeaders;
import org.glassfish.hk2.api.Factory;

public class ConfigurationApiFactory implements Factory<ConfigurationApi> {
  private static String dbRoot;
  @Context private HttpHeaders headers;

  public static void setDbRoot(String dbRoot) {
    ConfigurationApiFactory.dbRoot = dbRoot;
  }

  @Override
  public ConfigurationApi provide() {
    return new ConfigurationApi(ConfigurationApiFactory.dbRoot);
  }

  @Override
  public void dispose(ConfigurationApi service) {
    /* noop */
  }
}

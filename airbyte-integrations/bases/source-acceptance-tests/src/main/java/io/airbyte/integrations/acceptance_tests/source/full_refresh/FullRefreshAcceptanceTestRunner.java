package io.airbyte.integrations.acceptance_tests.source;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public class FullRefreshAcceptanceTestRunner extends FullRefreshAcceptanceTest {
  public static class Config {
    String connectorImage;
    JsonNode connectorConfig;
    ConfiguredAirbyteCatalog configuredCatalog;

    public Config(String connectorImage, JsonNode connectorConfig, ConfiguredAirbyteCatalog configuredCatalog) {
      this.connectorImage = connectorImage;
      this.connectorConfig = connectorConfig;
      this.configuredCatalog = configuredCatalog;
    }
  }
  
  public static Config CONFIG;

  @Override protected String getConnectorImage() {
    return CONFIG.connectorImage;
  }

  @Override
  protected JsonNode getConnectorConfig() {
    return CONFIG.connectorConfig;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredAirbyteCatalog() {
    return CONFIG.configuredCatalog;
  }
}

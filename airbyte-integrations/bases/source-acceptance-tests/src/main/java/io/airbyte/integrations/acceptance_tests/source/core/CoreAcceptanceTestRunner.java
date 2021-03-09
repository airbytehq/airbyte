package io.airbyte.integrations.acceptance_tests.source.core;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public class CoreAcceptanceTestRunner extends CoreAcceptanceTest {

  public static class Config {

    public Config(String connectorImage,
                  JsonNode expectedSpec,
                  JsonNode validConfig,
                  JsonNode invalidConfig,
                  ConfiguredAirbyteCatalog configuredCatalog) {
      this.connectorImage = connectorImage;
      this.expectedSpec = expectedSpec;
      this.validConfig = validConfig;
      this.invalidConfig = invalidConfig;
      this.configuredCatalog = configuredCatalog;
    }

    String connectorImage;
    JsonNode expectedSpec;
    JsonNode validConfig;
    JsonNode invalidConfig;
    ConfiguredAirbyteCatalog configuredCatalog;
  }

  public static Config CONFIG;

  protected JsonNode getValidConfig() {
    return CONFIG.validConfig;
  }

  @Override protected JsonNode getInvalidConfig() {
    return CONFIG.invalidConfig;
  }

  protected JsonNode getExpectedSpec() {
    return CONFIG.expectedSpec;
  }

  protected String getConnectorImage() {
    return CONFIG.connectorImage;
  }

  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CONFIG.configuredCatalog;
  }
}

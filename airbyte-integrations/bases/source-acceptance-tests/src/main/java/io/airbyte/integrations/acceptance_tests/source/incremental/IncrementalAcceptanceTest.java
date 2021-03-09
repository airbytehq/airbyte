package io.airbyte.integrations.acceptance_tests.source;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.junit.jupiter.api.Test;

public abstract class IncrementalAcceptanceTest {

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
  
  protected abstract String getConnectorImage();

  protected abstract JsonNode getConnectorConfig();

  protected abstract ConfiguredAirbyteCatalog getConfiguredCatalog();

  @Test
  public void todo() {
  }
}

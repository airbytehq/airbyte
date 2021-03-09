package io.airbyte.integrations.acceptance_tests.source;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.junit.jupiter.api.Test;

public abstract class CoreAcceptanceTest {

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

  protected abstract JsonNode getValidConfig();

  protected abstract JsonNode getInvalidConfig();

  protected abstract JsonNode getExpectedSpec();

  protected abstract String getConnectorImage();

  protected abstract ConfiguredAirbyteCatalog getConfiguredCatalog();

  @Test
  public void todo() {
  }
}

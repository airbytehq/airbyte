package io.airbyte.integrations.acceptance_tests.source;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public class CoreAcceptanceTestRunner extends CoreAcceptanceTest{
  public static Config CONFIG;

  protected JsonNode getValidConfig(){
    return CONFIG.validConfig;
  }

  @Override protected JsonNode getInvalidConfig() {
    return CONFIG.invalidConfig;
  }

  protected JsonNode getExpectedSpec(){
    return CONFIG.expectedSpec;
  }

  protected String getConnectorImage(){
    return CONFIG.connectorImage;
  }

  protected ConfiguredAirbyteCatalog getConfiguredCatalog(){
    return CONFIG.configuredCatalog;
  }
}

package io.airbyte.integrations.acceptance_tests.source;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public class IncrementalAcceptanceTestRunner extends IncrementalAcceptanceTest {

  public static Config CONFIG;

  @Override protected String getConnectorImage() {
    return CONFIG.connectorImage;
  }

  @Override
  protected JsonNode getConnectorConfig() {
    return CONFIG.connectorConfig;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CONFIG.configuredCatalog;
  }
}

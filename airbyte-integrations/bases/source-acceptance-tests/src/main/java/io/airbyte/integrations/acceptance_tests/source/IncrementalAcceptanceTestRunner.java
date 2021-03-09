package io.airbyte.integrations.acceptance_tests.source;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public class IncrementalAcceptanceTestRunner extends IncrementalAccTest {

  public static JsonNode CONNECTOR_CONFIG;
  public static ConfiguredAirbyteCatalog CONFIGURED_CATALOG;

  @Override
  protected JsonNode getConnectorConfig() {
    return CONNECTOR_CONFIG;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CONFIGURED_CATALOG;
  }
}

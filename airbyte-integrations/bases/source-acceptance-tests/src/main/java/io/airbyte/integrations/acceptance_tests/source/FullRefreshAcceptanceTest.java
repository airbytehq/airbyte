package io.airbyte.integrations.acceptance_tests.source;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.junit.jupiter.api.Test;

public abstract class FullRefreshAcceptanceTest {

  public static JsonNode CONNECTOR_CONFIG;
  public static ConfiguredAirbyteCatalog CONFIGURED_CATALOG;
  
  protected abstract JsonNode getConnectorConfig();
  
  protected abstract ConfiguredAirbyteCatalog getConfiguredAirbyteCatalog();
  
  @Test
  public void todo(){
  }
}

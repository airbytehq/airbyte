package io.airbyte.integrations.acceptance_tests.source.incremental;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.junit.jupiter.api.Test;

public abstract class IncrementalAcceptanceTest {
  
  protected abstract String getConnectorImage();

  protected abstract JsonNode getConnectorConfig();

  protected abstract ConfiguredAirbyteCatalog getConfiguredCatalog();

  @Test
  public void todo() {
  }
}

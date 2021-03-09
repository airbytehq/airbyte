package io.airbyte.integrations.acceptance_tests.source.full_refresh;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.junit.jupiter.api.Test;

public abstract class FullRefreshAcceptanceTest {
  protected abstract String getConnectorImage();

  protected abstract JsonNode getConnectorConfig();

  protected abstract ConfiguredAirbyteCatalog getConfiguredAirbyteCatalog();

  @Test
  public void todo() {
  }
}

package io.airbyte.integrations.acceptance_tests.source.core;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.junit.jupiter.api.Test;

public abstract class CoreAcceptanceTest {
  protected abstract JsonNode getValidConfig();

  protected abstract JsonNode getInvalidConfig();

  protected abstract JsonNode getExpectedSpec();

  protected abstract String getConnectorImage();

  protected abstract ConfiguredAirbyteCatalog getConfiguredCatalog();

  @Test
  public void todo() {
  }
}

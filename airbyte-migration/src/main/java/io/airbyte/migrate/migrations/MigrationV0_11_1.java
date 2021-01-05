package io.airbyte.migrate.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.migrate.Migration;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;

public class MigrationV0_11_1 extends MigrationV0_11_0 implements Migration {

  @Override
  public String getVersion() {
    return "v0.11.1-alpha";
  }

  @Override
  public Map<String, JsonNode> getInputSchema() {
    return new MigrationV0_11_0().getInputSchema();
  }

  @Override
  public Map<String, JsonNode> getOutputSchema() {
    return getInputSchema();
  }

  // no op migration.
  @Override
  public void migrate(Map<String, Stream<JsonNode>> inputData, Map<String, Consumer<JsonNode>> outputData) {
    for (Map.Entry<String, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());
      entry.getValue().forEach(recordConsumer);
    }
  }
}

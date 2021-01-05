package io.airbyte.migrate.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.CaseFormat;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.migrate.Migration;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;

public class MigrationV0_11_0 implements Migration {

  @Override
  public String getVersion() {
    return "v0.11.0-alpha";
  }

  @Override
  public Map<String, JsonNode> getInputSchema() {
    final Map<String, JsonNode> schemas = new HashMap<>();

    // add config schemas.
    schemas.putAll(getNameToSchemasFromPath(Path.of("migrations/migrationV0_11_0/config")));
    // add db schemas.
    schemas.putAll(getNameToSchemasFromPath(Path.of("migrations/migrationV0_11_0/jobs")));

    return schemas;
  }

  private Map<String, JsonNode> getNameToSchemasFromPath(Path path) {
    final Map<String, JsonNode> schemas = new HashMap<>();

    final Path pathToSchemas = JsonSchemas.prepareSchemas(path.toString(), MigrationV0_11_0.class);
    IOs.listFiles(pathToSchemas)
        .stream()
        .map(f -> JsonSchemaValidator.getSchema(f.toFile()))
        .forEach(j -> schemas.put(CaseFormat.UPPER_CAMEL.to(CaseFormat.UPPER_UNDERSCORE, j.get("title").asText()), j));

    return schemas;
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

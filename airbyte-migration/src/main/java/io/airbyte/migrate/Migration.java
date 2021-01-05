package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;

public interface Migration {
  String getVersion();

  Map<String, JsonNode> getInputSchema();

  Map<String, JsonNode> getOutputSchema();

  void migrate(Map<String, Stream<JsonNode>> inputData, Map<String, Consumer<JsonNode>> outputData);

}

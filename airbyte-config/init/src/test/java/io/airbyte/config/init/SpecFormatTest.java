package io.airbyte.config.init;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

@Slf4j
public class SpecFormatTest {

  @Test
  void testOnAllExistingConfig() throws IOException, JsonValidationException {
    final ConfigPersistence configPersistence = YamlSeedConfigPersistence.getDefault();

    log.error("Sources");
    final List<JsonNode> latestSourcesSpecs = configPersistence.listConfigs(
        ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class)
        .stream()
        .map(standardSourceDefinition -> standardSourceDefinition.getSpec().getConnectionSpecification())
        .toList();

    latestSourcesSpecs.forEach(
        spec -> {
          try {
            JsonSchemas.traverseJsonSchema(spec, (node, path) -> {});
          } catch (final Exception e) {
            log.error("failed on: " + spec.toString(), e);
          }
        }
    );

    log.error("Destinations");
    final List<JsonNode> latestDestinationSpecs = configPersistence.listConfigs(
            ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class)
        .stream()
        .map(standardDestinationDefinition -> standardDestinationDefinition.getSpec().getConnectionSpecification())
        .toList();

    latestSourcesSpecs.forEach(
        spec -> {
          try {
            JsonSchemas.traverseJsonSchema(spec, (node, path) -> {});
          } catch (final Exception e) {
            log.error("failed on: " + spec.toString(), e);
          }
        }
    );
  }
}

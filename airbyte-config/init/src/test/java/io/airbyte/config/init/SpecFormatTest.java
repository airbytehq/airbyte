/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import lombok.extern.slf4j.Slf4j;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

@Slf4j
class SpecFormatTest {

  @Test
  void testOnAllExistingConfig() throws IOException, JsonValidationException {
    final ConfigPersistence configPersistence = new YamlSeedConfigPersistence(YamlSeedConfigPersistence.DEFAULT_SEED_DEFINITION_RESOURCE_CLASS);

    final List<JsonNode> sourceSpecs = configPersistence.listConfigs(
        ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class)
        .stream()
        .map(standardSourceDefinition -> standardSourceDefinition.getSpec().getConnectionSpecification())
        .toList();

    final List<JsonNode> destinationSpecs = configPersistence.listConfigs(
        ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class)
        .stream()
        .map(standardDestinationDefinition -> standardDestinationDefinition.getSpec().getConnectionSpecification())
        .toList();

    final List<JsonNode> allSpecs = new ArrayList<>();

    allSpecs.addAll(sourceSpecs);
    allSpecs.addAll(destinationSpecs);

    Assertions.assertThat(allSpecs)
        .flatMap(spec -> {
          try {
            JsonSchemas.traverseJsonSchema(spec, (node, path) -> {});
            return Collections.emptyList();
          } catch (final Exception e) {
            log.error("failed on: " + spec.toString(), e);
            return List.of(e);
          }
        })
        .isEmpty();
  }

}

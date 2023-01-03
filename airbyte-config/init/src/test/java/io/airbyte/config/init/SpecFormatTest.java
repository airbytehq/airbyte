/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
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
    final DefinitionsProvider definitionsProvider = new LocalDefinitionsProvider(LocalDefinitionsProvider.DEFAULT_SEED_DEFINITION_RESOURCE_CLASS);

    final List<JsonNode> sourceSpecs = definitionsProvider.getSourceDefinitions()
        .stream()
        .map(standardSourceDefinition -> standardSourceDefinition.getSpec().getConnectionSpecification())
        .toList();

    final List<JsonNode> destinationSpecs = definitionsProvider.getDestinationDefinitions()
        .stream()
        .map(standardDestinationDefinition -> standardDestinationDefinition.getSpec().getConnectionSpecification())
        .toList();

    final List<JsonNode> allSpecs = new ArrayList<>();

    allSpecs.addAll(sourceSpecs);
    allSpecs.addAll(destinationSpecs);

    Assertions.assertThat(allSpecs)
        .flatMap(spec -> {
          try {
            if (!JsonSecretsProcessor.isValidJsonSchema(spec)) {
              throw new RuntimeException("Fail JsonSecretsProcessor validation");
            }
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

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.specs;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DockerImageSpec;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class CombinedConnectorCatalogGeneratorTest {

  private static final UUID DEF_ID1 = UUID.randomUUID();
  private static final UUID DEF_ID2 = UUID.randomUUID();
  private static final String CONNECTOR_NAME1 = "connector1";
  private static final String CONNECTOR_NAME2 = "connector2";
  private static final String DOCUMENTATION_URL = "https://www.example.com";
  private static final String DOCKER_REPOSITORY1 = "airbyte/connector1";
  private static final String DOCKER_REPOSITORY2 = "airbyte/connector2";
  private static final String DOCKER_TAG1 = "0.1.0";
  private static final String DOCKER_TAG2 = "0.2.0";

  private CombinedConnectorCatalogGenerator catalogGenerator;

  @BeforeEach
  void setup() {
    catalogGenerator = new CombinedConnectorCatalogGenerator();
  }

  @Test
  void testMergeSpecsIntoDefinitions() {
    final StandardDestinationDefinition destinationDefinition1 = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DEF_ID1)
        .withDockerRepository(DOCKER_REPOSITORY1)
        .withDockerImageTag(DOCKER_TAG1)
        .withName(CONNECTOR_NAME1)
        .withDocumentationUrl(DOCUMENTATION_URL)
        .withSpec(new ConnectorSpecification());
    final StandardDestinationDefinition destinationDefinition2 = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DEF_ID2)
        .withDockerRepository(DOCKER_REPOSITORY2)
        .withDockerImageTag(DOCKER_TAG2)
        .withName(CONNECTOR_NAME2)
        .withDocumentationUrl(DOCUMENTATION_URL)
        .withSpec(new ConnectorSpecification());
    final DockerImageSpec destinationSpec1 = new DockerImageSpec().withDockerImage(DOCKER_REPOSITORY1 + ":" + DOCKER_TAG1)
        .withSpec(new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of(
            "foo1",
            "bar1"))));
    final DockerImageSpec destinationSpec2 = new DockerImageSpec().withDockerImage(DOCKER_REPOSITORY2 + ":" + DOCKER_TAG2)
        .withSpec(new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of(
            "foo2",
            "bar2"))));

    final List<JsonNode> definitions = List.of(Jsons.jsonNode(destinationDefinition1), Jsons.jsonNode(destinationDefinition2));
    final List<JsonNode> specs = List.of(Jsons.jsonNode(destinationSpec1), Jsons.jsonNode(destinationSpec2));

    catalogGenerator.mergeSpecsIntoDefinitions(definitions, specs, ConfigSchema.STANDARD_DESTINATION_DEFINITION);

    final StandardDestinationDefinition expectedDefinition1 = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DEF_ID1)
        .withDockerRepository(DOCKER_REPOSITORY1)
        .withDockerImageTag(DOCKER_TAG1)
        .withName(CONNECTOR_NAME1)
        .withDocumentationUrl(DOCUMENTATION_URL)
        .withSpec(destinationSpec1.getSpec());

    final StandardDestinationDefinition expectedDefinition2 = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DEF_ID2)
        .withDockerRepository(DOCKER_REPOSITORY2)
        .withDockerImageTag(DOCKER_TAG2)
        .withName(CONNECTOR_NAME2)
        .withDocumentationUrl(DOCUMENTATION_URL)
        .withSpec(destinationSpec2.getSpec());

    assertEquals(Jsons.jsonNode(expectedDefinition1), definitions.get(0));
    assertEquals(Jsons.jsonNode(expectedDefinition2), definitions.get(1));
  }

  @Test
  void testMergeSpecsIntoDefinitionsThrowsOnMissingSpec() {
    final StandardDestinationDefinition destinationDefinition1 = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DEF_ID1)
        .withDockerRepository(DOCKER_REPOSITORY1)
        .withDockerImageTag(DOCKER_TAG1)
        .withName(CONNECTOR_NAME1)
        .withDocumentationUrl(DOCUMENTATION_URL)
        .withSpec(new ConnectorSpecification());
    final List<JsonNode> definitions = List.of(Jsons.jsonNode(destinationDefinition1));
    final List<JsonNode> specs = List.of();

    assertThrows(UnsupportedOperationException.class,
        () -> catalogGenerator.mergeSpecsIntoDefinitions(definitions, specs, ConfigSchema.STANDARD_DESTINATION_DEFINITION));
  }

  @Test
  void testMergeSpecsIntoDefinitionsThrowsOnInvalidFormat() {
    final JsonNode invalidDefinition = Jsons.jsonNode(ImmutableMap.of("dockerRepository", DOCKER_REPOSITORY1, "dockerImageTag", DOCKER_TAG1));
    final DockerImageSpec destinationSpec = new DockerImageSpec().withDockerImage(DOCKER_REPOSITORY1 + ":" + DOCKER_TAG1)
        .withSpec(new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of(
            "foo1",
            "bar1"))));

    final List<JsonNode> definitions = List.of(Jsons.jsonNode(invalidDefinition));
    final List<JsonNode> specs = List.of(Jsons.jsonNode(destinationSpec));

    assertThrows(RuntimeException.class,
        () -> catalogGenerator.mergeSpecsIntoDefinitions(definitions, specs, ConfigSchema.STANDARD_DESTINATION_DEFINITION));
  }

}

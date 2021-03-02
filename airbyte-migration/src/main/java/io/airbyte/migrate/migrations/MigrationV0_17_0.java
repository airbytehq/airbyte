/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.migrate.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.io.IOException;
import java.util.Iterator;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This migration forces upgrading all sources and destinations connectors to be at least equal to
 * or greater than 0.2.0
 *
 * This is because as part of Airbyte V0.17.0-alpha, we made changes to the JSON validation
 * parsers/serializers/deserializers from all connectors to allow for unknown properties, thus
 * bumping their versions to v0.2.0 as part of that release.
 *
 * This is required in case we want to perform modifications to the Airbyte protocol in the future
 * by adding new properties. Connectors that are not using these additional properties yet, should
 * ignore them but keep working as usual instead of throwing json validation errors.
 */
public class MigrationV0_17_0 extends BaseMigration implements Migration {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationV0_17_0.class);

  private static final ResourceId STANDARD_SOURCE_DEFINITION_RESOURCE_ID =
      ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SOURCE_DEFINITION");
  private static final ResourceId STANDARD_DESTINATION_DEFINITION_RESOURCE_ID =
      ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_DESTINATION_DEFINITION");

  private static final String DESTINATION_SEEDS = "migrations/migrationV0_17_0/airbyte_config/destination_definitions.yaml";
  private static final String SOURCE_SEEDS = "migrations/migrationV0_17_0/airbyte_config/source_definitions.yaml";

  private final Migration previousMigration;

  public MigrationV0_17_0(Migration previousMigration) {
    super(previousMigration);
    this.previousMigration = previousMigration;
  }

  @Override
  public String getVersion() {
    return "0.17.0-alpha";
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    return previousMigration.getOutputSchema();
  }

  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData, Map<ResourceId, Consumer<JsonNode>> outputData) {
    try {
      final JsonNode sourceConnectors = Yamls.deserialize(MoreResources.readResource(SOURCE_SEEDS));
      final JsonNode destinationConnectors = Yamls.deserialize(MoreResources.readResource(DESTINATION_SEEDS));

      for (final Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
        final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());

        entry.getValue().forEach(r -> {
          if (entry.getKey().equals(STANDARD_SOURCE_DEFINITION_RESOURCE_ID)) {
            ((ObjectNode) r).set("dockerImageTag", getDockerImageTag(sourceConnectors, "sourceDefinitionId", r));
          } else if (entry.getKey().equals(STANDARD_DESTINATION_DEFINITION_RESOURCE_ID)) {
            ((ObjectNode) r).set("dockerImageTag", getDockerImageTag(destinationConnectors, "destinationDefinitionId", r));
          }
          recordConsumer.accept(r);
        });
      }
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private JsonNode getDockerImageTag(final JsonNode connectors, final String definitionId, final JsonNode node) {
    final JsonNode connectorName = node.get("name");
    final JsonNode dockerImageTag = node.get("dockerImageTag");
    final JsonNode connectorDefinitionId = node.get(definitionId);
    final AirbyteVersion connectorVersion = new AirbyteVersion(dockerImageTag.asText());

    final Iterator<JsonNode> it = connectors.elements();
    while (it.hasNext()) {
      final JsonNode standardConnector = it.next();
      if (standardConnector.get(definitionId).equals(connectorDefinitionId)) {
        final JsonNode requiredDockerTag = standardConnector.get("dockerImageTag");
        final AirbyteVersion requiredVersion = new AirbyteVersion(requiredDockerTag.asText());
        if (connectorVersion.patchVersionCompareTo(requiredVersion) >= 0) {
          return dockerImageTag;
        } else {
          LOGGER.debug(String.format("Bump connector %s version from %s to %s", connectorName, dockerImageTag, requiredDockerTag));
          return requiredDockerTag;
        }
      }
    }
    return dockerImageTag;
  }

}

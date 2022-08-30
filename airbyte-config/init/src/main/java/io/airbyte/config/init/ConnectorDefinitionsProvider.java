/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.BooleanNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public abstract class ConnectorDefinitionsProvider {

  private ImmutableMap<ConfigSchema, Map<String, JsonNode>> allDefinitions;

  protected static final ImmutableMap<ConfigSchema, Map<String, JsonNode>> emptyDefinitions =
      ImmutableMap.<ConfigSchema, Map<String, JsonNode>>builder()
          .put(ConfigSchema.STANDARD_SOURCE_DEFINITION, Collections.emptyMap())
          .put(ConfigSchema.STANDARD_DESTINATION_DEFINITION, Collections.emptyMap())
          .build();

  // TODO will be called automatically by the dependency injection framework on object creation
  public abstract void initialize() throws InterruptedException;

  protected void setAllDefinitions(final ImmutableMap<ConfigSchema, Map<String, JsonNode>> allDefinitions) {
    this.allDefinitions = allDefinitions;
  }

  public <T> T getDefinition(final ConfigSchema definitionType, final String definitionId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    final Map<String, JsonNode> connectors = allDefinitions.get(definitionType);
    if (connectors == null) {
      throw new UnsupportedOperationException("There is no definition for " + definitionType.name());
    }
    final JsonNode definition = connectors.get(definitionId);
    if (definition == null) {
      throw new ConfigNotFoundException(definitionType, definitionId);
    }
    return Jsons.object(definition, clazz);
  }

  public Map<String, Stream<JsonNode>> dumpDefinitions() {
    return allDefinitions.entrySet().stream().collect(Collectors.toMap(
        e -> e.getKey().name(),
        e -> e.getValue().values().stream()));
  }

  protected static JsonNode addMissingPublicField(final JsonNode definitionJson) {
    final JsonNode currPublic = definitionJson.get("public");
    if (currPublic == null || currPublic.isNull()) {
      // definitions loaded from seed yamls are by definition public
      ((ObjectNode) definitionJson).set("public", BooleanNode.TRUE);
    }
    return definitionJson;
  }

  protected static JsonNode addMissingCustomField(final JsonNode definitionJson) {
    final JsonNode currCustom = definitionJson.get("custom");
    if (currCustom == null || currCustom.isNull()) {
      // definitions loaded from seed yamls are by definition not custom
      ((ObjectNode) definitionJson).set("custom", BooleanNode.FALSE);
    }
    return definitionJson;
  }

  protected static JsonNode addMissingTombstoneField(final JsonNode definitionJson) {
    final JsonNode currTombstone = definitionJson.get("tombstone");
    if (currTombstone == null || currTombstone.isNull()) {
      ((ObjectNode) definitionJson).set("tombstone", BooleanNode.FALSE);
    }
    return definitionJson;
  }

}

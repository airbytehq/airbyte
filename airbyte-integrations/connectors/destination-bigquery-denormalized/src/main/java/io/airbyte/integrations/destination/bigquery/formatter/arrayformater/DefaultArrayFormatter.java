/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter.arrayformater;

import static io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryDenormalizedRecordFormatter.PROPERTIES_FIELD;
import static io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryDenormalizedRecordFormatter.TYPE_FIELD;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

public class DefaultArrayFormatter implements ArrayFormatter {

  public static final String NESTED_ARRAY_FIELD = "big_query_array";
  public static final String ARRAY_ITEMS_FIELD = "items";

  @Override
  public void populateEmptyArrays(final JsonNode node) {
    findArrays(node).forEach(jsonNode -> {
      if (!jsonNode.has(ARRAY_ITEMS_FIELD)) {
        final ObjectNode nodeToChange = (ObjectNode) jsonNode;
        nodeToChange.putObject(ARRAY_ITEMS_FIELD).putArray(TYPE_FIELD).add("string");
      }
    });
  }

  @Override
  public void surroundArraysByObjects(final JsonNode node) {
    findArrays(node).forEach(
        jsonNode -> {
          if (isAirbyteArray(jsonNode.get(ARRAY_ITEMS_FIELD))) {
            final ObjectNode arrayNode = jsonNode.get(ARRAY_ITEMS_FIELD).deepCopy();
            final ObjectNode originalNode = (ObjectNode) jsonNode;

            originalNode.remove(ARRAY_ITEMS_FIELD);
            final ObjectNode itemsNode = originalNode.putObject(ARRAY_ITEMS_FIELD);
            itemsNode.putArray(TYPE_FIELD).add("object");
            itemsNode.putObject(PROPERTIES_FIELD).putObject(NESTED_ARRAY_FIELD).setAll(arrayNode);

            surroundArraysByObjects(originalNode.get(ARRAY_ITEMS_FIELD));
          }
        });
  }

  @Override
  public JsonNode formatArrayItems(List<JsonNode> arrayItems) {
    return Jsons
        .jsonNode(arrayItems.stream().map(node -> (node.isArray() ? Jsons.jsonNode(ImmutableMap.of(NESTED_ARRAY_FIELD, node)) : node)).toList());
  }

  protected List<JsonNode> findArrays(final JsonNode node) {
    if (node != null) {
      return node.findParents(TYPE_FIELD).stream()
          .filter(this::isAirbyteArray)
          .collect(Collectors.toList());
    } else {
      return Collections.emptyList();
    }
  }

  protected boolean isAirbyteArray(final JsonNode node) {
    final JsonNode type = node.get(TYPE_FIELD);
    if (type.isArray()) {
      final ArrayNode typeNode = (ArrayNode) type;
      for (final JsonNode arrayTypeNode : typeNode) {
        if (arrayTypeNode.isTextual() && arrayTypeNode.textValue().equals("array")) {
          return true;
        }
      }
    } else if (type.isTextual()) {
      return node.asText().equals("array");
    }
    return false;
  }

}

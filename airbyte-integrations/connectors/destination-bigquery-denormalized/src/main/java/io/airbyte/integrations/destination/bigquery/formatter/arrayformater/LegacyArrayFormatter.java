/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter.arrayformater;

import static io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryDenormalizedRecordFormatter.PROPERTIES_FIELD;
import static io.airbyte.integrations.destination.bigquery.formatter.util.FormatterUtil.ARRAY_ITEMS_FIELD;
import static io.airbyte.integrations.destination.bigquery.formatter.util.FormatterUtil.NESTED_ARRAY_FIELD;
import static io.airbyte.integrations.destination.bigquery.formatter.util.FormatterUtil.TYPE_FIELD;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.bigquery.formatter.util.FormatterUtil;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

public class LegacyArrayFormatter extends DefaultArrayFormatter {

  @Override
  public void surroundArraysByObjects(final JsonNode node) {
    findArrays(node).forEach(
        jsonNode -> {
          final JsonNode arrayNode = jsonNode.deepCopy();

          final ObjectNode newNode = (ObjectNode) jsonNode;
          newNode.removeAll();
          newNode.putArray(TYPE_FIELD).add("object");
          newNode.putObject(PROPERTIES_FIELD).set(NESTED_ARRAY_FIELD, arrayNode);

          surroundArraysByObjects(arrayNode.get(ARRAY_ITEMS_FIELD));
        });
  }

  @Override
  protected List<JsonNode> findArrays(final JsonNode node) {
    if (node != null) {
      return node.findParents(TYPE_FIELD).stream()
          .filter(FormatterUtil::isAirbyteArray)
          .collect(Collectors.toList());
    } else {
      return Collections.emptyList();
    }
  }

  @Override
  public JsonNode formatArrayItems(List<JsonNode> arrayItems) {
    return Jsons.jsonNode(ImmutableMap.of(NESTED_ARRAY_FIELD, arrayItems));
  }

}

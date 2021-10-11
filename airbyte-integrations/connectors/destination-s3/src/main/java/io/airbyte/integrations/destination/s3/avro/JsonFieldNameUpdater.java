/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Map;

/**
 * This helper class tracks whether a Json has special field name that needs to be replaced with a
 * standardized one, and can perform the replacement when necessary.
 */
public class JsonFieldNameUpdater {

  // A map from original name to standardized name.
  private final Map<String, String> standardizedNames;

  public JsonFieldNameUpdater(Map<String, String> standardizedNames) {
    this.standardizedNames = ImmutableMap.copyOf(standardizedNames);
  }

  public boolean hasNameUpdate() {
    return standardizedNames.size() > 0;
  }

  public JsonNode getJsonWithStandardizedFieldNames(JsonNode input) {
    if (!hasNameUpdate()) {
      return input;
    }
    String jsonString = Jsons.serialize(input);
    for (Map.Entry<String, String> entry : standardizedNames.entrySet()) {
      jsonString = jsonString.replaceAll(quote(entry.getKey()), quote(entry.getValue()));
    }
    return Jsons.deserialize(jsonString);
  }

  public JsonNode getJsonWithOriginalFieldNames(JsonNode input) {
    if (!hasNameUpdate()) {
      return input;
    }
    String jsonString = Jsons.serialize(input);
    for (Map.Entry<String, String> entry : standardizedNames.entrySet()) {
      jsonString = jsonString.replaceAll(quote(entry.getValue()), quote(entry.getKey()));
    }
    return Jsons.deserialize(jsonString);
  }

  @Override
  public String toString() {
    return standardizedNames.toString();
  }

  private static String quote(String input) {
    return "\"" + input + "\"";
  }

}

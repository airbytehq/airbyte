/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Map;

/**
 * This helper class is for testing only. It tracks the original and standardized names, and revert
 * them when necessary, so that the tests can correctly compare the generated json with the original
 * input.
 */
public class JsonFieldNameUpdater {

  // A map from original name to standardized name.
  private final Map<String, String> standardizedNames;

  public JsonFieldNameUpdater(final Map<String, String> standardizedNames) {
    this.standardizedNames = ImmutableMap.copyOf(standardizedNames);
  }

  public JsonNode getJsonWithOriginalFieldNames(final JsonNode input) {
    if (standardizedNames.size() == 0) {
      return input;
    }
    String jsonString = Jsons.serialize(input);
    for (final Map.Entry<String, String> entry : standardizedNames.entrySet()) {
      jsonString = jsonString.replaceAll(quote(entry.getValue()), quote(entry.getKey()));
    }
    return Jsons.deserialize(jsonString);
  }

  @Override
  public String toString() {
    return standardizedNames.toString();
  }

  private static String quote(final String input) {
    return "\"" + input + "\"";
  }

}

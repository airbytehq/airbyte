/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination.comparator;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.List;
import java.util.function.Function;

public class ComparatorUtils {

  public static JsonNode getActualValueByExpectedKey(final String expectedKey,
                                                     final JsonNode actualJsonNode,
                                                     final Function<String, List<String>> nameResolver) {
    for (final String actualKey : nameResolver.apply(expectedKey)) {
      if (actualJsonNode.has(actualKey)) {
        return actualJsonNode.get(actualKey);
      }
    }
    return null;
  }

}

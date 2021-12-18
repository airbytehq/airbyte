/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.json;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.util.MoreIterators;
import java.util.Optional;
import java.util.Set;
import java.util.function.BiFunction;

public class Secrets {

  static final String AIRBYTE_SECRET_FIELD = "airbyte_secret";
  static final String SECRETS_MASK = "**********";

  // given a schema and an object always clobber and replace with ***
  // given a schema and an object if raw secret replace with a string and then track raw and secret,
  // otherwise do nothign

  public static JsonNode maskAllSecrets(final JsonNode json, final JsonNode schema) {
    final Set<String> pathsWithSecrets = JsonSchemas.collectJsonPathsThatMeetCondition(
        schema,
        node -> MoreIterators.toList(node.fields())
            .stream()
            .anyMatch(field -> field.getKey().equals(AIRBYTE_SECRET_FIELD)));

    System.out.println("pathsWithSecrets = " + pathsWithSecrets);
    JsonNode copy = Jsons.clone(json);
    for (final String path : pathsWithSecrets) {
      copy = JsonPaths.replaceAtString(copy, path, SECRETS_MASK);
    }

    return copy;
  }

  public static JsonNode replaceAt(final JsonNode json, final String jsonPath, final BiFunction<JsonNode, String, JsonNode> replacementFunction) {
    return JsonPaths.replaceAt(json, jsonPath, replacementFunction);
  }

  public static Optional<JsonNode> getSingleValue(final JsonNode json, final String jsonPath) {
    return JsonPaths.getSingleValue(json, jsonPath);
  }
}

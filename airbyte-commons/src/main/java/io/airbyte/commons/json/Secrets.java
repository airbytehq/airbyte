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

  /**
   * Given a JSONSchema object and an object that conforms to that schema, obfuscate all fields in the
   * object that are a secret.
   *
   * @param json - json object that conforms to the schema
   * @param schema - jsonschema object
   * @return json object with all secrets masked.
   */
  public static JsonNode maskAllSecrets(final JsonNode json, final JsonNode schema) {
    final Set<String> pathsWithSecrets = JsonSchemas.collectJsonPathsThatMeetCondition(
        schema,
        node -> MoreIterators.toList(node.fields())
            .stream()
            .anyMatch(field -> field.getKey().equals(AIRBYTE_SECRET_FIELD)));

    JsonNode copy = Jsons.clone(json);
    for (final String path : pathsWithSecrets) {
      copy = JsonPaths.replaceAtString(copy, path, SECRETS_MASK);
    }

    return copy;
  }

  public static JsonNode replaceSecretAt(final JsonNode json,
                                         final String jsonPath,
                                         final BiFunction<JsonNode, String, JsonNode> replacementFunction) {
    return JsonPaths.replaceAt(json, jsonPath, replacementFunction);
  }

  public static Optional<JsonNode> getSingleValue(final JsonNode json, final String jsonPath) {
    return JsonPaths.getSingleValue(json, jsonPath);
  }

}

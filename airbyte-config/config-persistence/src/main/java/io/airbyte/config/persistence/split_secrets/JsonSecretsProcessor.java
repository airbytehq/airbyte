/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.constants.AirbyteSecretConstants;
import io.airbyte.commons.json.JsonPaths;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import lombok.Builder;
import lombok.extern.slf4j.Slf4j;

@Builder
@SuppressWarnings({"PMD.CognitiveComplexity", "PMD.CyclomaticComplexity"})
@Slf4j
public class JsonSecretsProcessor {

  @Builder.Default
  final private Boolean copySecrets = false;

  protected static final JsonSchemaValidator VALIDATOR = new JsonSchemaValidator();

  static final String PROPERTIES_FIELD = "properties";
  static final String TYPE_FIELD = "type";
  static final String ARRAY_TYPE_FIELD = "array";
  static final String ITEMS_FIELD = "items";
  static final String ONE_OF_FIELD = "oneOf";

  /**
   * Returns a copy of the input object wherein any fields annotated with "airbyte_secret" in the
   * input schema are masked.
   * <p>
   * This method masks secrets both at the top level of the configuration object and in nested
   * properties in a oneOf.
   *
   * @param schema Schema containing secret annotations
   * @param obj Object containing potentially secret fields
   */
  public JsonNode prepareSecretsForOutput(final JsonNode obj, final JsonNode schema) {
    // todo (cgardens) this is not safe. should throw.
    // if schema is an object and has a properties field
    if (!isValidJsonSchema(schema)) {
      log.error("The schema is not valid, the secret can't be hidden");
      return obj;
    }

    return maskAllSecrets(obj, schema);
  }

  /**
   * Given a JSONSchema object and an object that conforms to that schema, obfuscate all fields in the
   * object that are a secret.
   *
   * @param json - json object that conforms to the schema
   * @param schema - jsonschema object
   * @return json object with all secrets masked.
   */
  public static JsonNode maskAllSecrets(final JsonNode json, final JsonNode schema) {
    final Set<String> pathsWithSecrets = JsonSchemas.collectPathsThatMeetCondition(
        schema,
        node -> MoreIterators.toList(node.fields())
            .stream()
            .anyMatch(field -> AirbyteSecretConstants.AIRBYTE_SECRET_FIELD.equals(field.getKey())))
        .stream()
        .map(JsonPaths::mapJsonSchemaPathToJsonPath)
        .collect(Collectors.toSet());

    JsonNode copy = Jsons.clone(json);
    for (final String path : pathsWithSecrets) {
      copy = JsonPaths.replaceAtString(copy, path, AirbyteSecretConstants.SECRETS_MASK);
    }

    return copy;
  }

  /**
   * Returns a copy of the destination object in which any secret fields (as denoted by the input
   * schema) found in the source object are added.
   * <p>
   * This method absorbs secrets both at the top level of the configuration object and in nested
   * properties in a oneOf.
   *
   * @param src The object potentially containing secrets
   * @param dst The object to absorb secrets into
   * @param schema Schema of objects
   * @return dst object with secrets absorbed from src object
   */
  // todo (cgardens) - figure out how to reused JsonSchemas and JsonPaths for this traversal as well.
  public JsonNode copySecrets(final JsonNode src, final JsonNode dst, final JsonNode schema) {
    if (copySecrets) {
      // todo (cgardens) this is not safe. should throw.
      if (!isValidJsonSchema(schema)) {
        return dst;
      }

      Preconditions.checkArgument(dst.isObject());
      Preconditions.checkArgument(src.isObject());

      final ObjectNode dstCopy = dst.deepCopy();
      return copySecretsRecursive(src, dstCopy, schema);
    }

    return src;
  }

  // This function is modifying dstCopy in place.
  private JsonNode copySecretsRecursive(final JsonNode src, JsonNode dstCopy, final JsonNode schema) {
    // todo (cgardens) this is not safe. should throw.
    if (!isValidJsonSchema(schema)) {
      return dstCopy;
    }

    Preconditions.checkArgument(dstCopy.isObject());
    Preconditions.checkArgument(src.isObject());

    final Optional<String> combinationKey = findJsonCombinationNode(schema);
    if (combinationKey.isPresent()) {
      final var arrayNode = (ArrayNode) schema.get(combinationKey.get());
      for (int i = 0; i < arrayNode.size(); i++) {
        final JsonNode childSchema = arrayNode.get(i);
        /*
         * when traversing a oneOf or anyOf if multiple schema in the oneOf or anyOf have the SAME key, but
         * a different type, then, without this test, we can try to apply the wrong schema to the object
         * resulting in errors because of type mismatches.
         */
        if (VALIDATOR.test(childSchema, dstCopy)) {
          // Absorb field values if any of the combination option is declaring it as secrets
          copySecretsRecursive(src, dstCopy, childSchema);
        }
      }
    } else {
      final ObjectNode properties = (ObjectNode) schema.get(PROPERTIES_FIELD);
      for (final String key : Jsons.keys(properties)) {
        // If the source or destination doesn't have this key then we have nothing to copy, so we should
        // skip to the next key.
        if (!src.has(key) || !dstCopy.has(key)) {
          continue;
        }

        final JsonNode fieldSchema = properties.get(key);
        // We only copy the original secret if the destination object isn't attempting to overwrite it
        // I.e. if the destination object's value is set to the mask, then we can copy the original secret
        if (JsonSecretsProcessor.isSecret(fieldSchema) && AirbyteSecretConstants.SECRETS_MASK.equals(dstCopy.get(key).asText())) {
          ((ObjectNode) dstCopy).set(key, src.get(key));

        } else {
          // Otherwise, this is just a plain old json node; recurse into it. If it's not actually an object,
          // the recursive call will exit immediately.
          final JsonNode copiedField = copySecretsRecursive(src.get(key), dstCopy.get(key), fieldSchema);
          ((ObjectNode) dstCopy).set(key, copiedField);
        }
      }
    }

    return dstCopy;
  }

  static boolean isSecret(final JsonNode obj) {
    return obj.isObject() && obj.has(AirbyteSecretConstants.AIRBYTE_SECRET_FIELD) && obj.get(AirbyteSecretConstants.AIRBYTE_SECRET_FIELD).asBoolean();
  }

  private static Optional<String> findJsonCombinationNode(final JsonNode node) {
    for (final String combinationNode : List.of("allOf", "anyOf", "oneOf")) {
      if (node.has(combinationNode) && node.get(combinationNode).isArray()) {
        return Optional.of(combinationNode);
      }
    }
    return Optional.empty();
  }

  @SuppressWarnings("BooleanMethodIsAlwaysInverted")
  @VisibleForTesting
  public static boolean isValidJsonSchema(final JsonNode schema) {
    return schema.isObject() && ((schema.has(PROPERTIES_FIELD) && schema.get(PROPERTIES_FIELD).isObject())
        || (schema.has(ONE_OF_FIELD) && schema.get(ONE_OF_FIELD).isArray()));
  }

}

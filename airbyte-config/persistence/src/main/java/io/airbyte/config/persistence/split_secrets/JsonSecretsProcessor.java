/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Optional;
import java.util.Queue;
import java.util.Set;
import lombok.Builder;
import lombok.Value;

@Builder
public class JsonSecretsProcessor {

  @Builder.Default
  private boolean maskSecrets = true;

  @Builder.Default
  private boolean copySecrets = true;

  protected static final JsonSchemaValidator VALIDATOR = new JsonSchemaValidator();

  @VisibleForTesting
  static String SECRETS_MASK = "**********";

  static final String AIRBYTE_SECRET_FIELD = "airbyte_secret";
  static final String PROPERTIES_FIELD = "properties";
  static final String TYPE_FIELD = "type";
  static final String ARRAY_TYPE_FIELD = "array";
  static final String ITEMS_FIELD = "items";

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
    if (maskSecrets) {
      // if schema is an object and has a properties field
      if (!canBeProcessed(schema)) {
        return obj;
      }

      final SecretKeys secretKeys = getAllSecretKeys(schema);
      return maskAllSecrets(obj, secretKeys);
    }

    return obj;
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
   * @param schema
   * @return
   */
  public JsonNode copySecrets(final JsonNode src, final JsonNode dst, final JsonNode schema) {
    if (copySecrets) {
      if (!canBeProcessed(schema)) {
        return dst;
      }
      Preconditions.checkArgument(dst.isObject());
      Preconditions.checkArgument(src.isObject());

      final ObjectNode dstCopy = dst.deepCopy();

      final ObjectNode properties = (ObjectNode) schema.get(PROPERTIES_FIELD);
      for (final String key : Jsons.keys(properties)) {
        // If the source object doesn't have this key then we have nothing to copy, so we should skip to the
        // next key.
        if (!src.has(key)) {
          continue;
        }

        final JsonNode fieldSchema = properties.get(key);
        // We only copy the original secret if the destination object isn't attempting to overwrite it
        // I.e. if the destination object's value is set to the mask, then we can copy the original secret
        if (JsonSecretsProcessor.isSecret(fieldSchema) && dst.has(key) && dst.get(key).asText().equals(SECRETS_MASK)) {
          dstCopy.set(key, src.get(key));
        } else if (dstCopy.has(key)) {
          // If the destination has this key, then we should consider copying it

          // Check if this schema is a combination node; if it is, find a matching sub-schema and copy based
          // on that sub-schema
          final var combinationKey = findJsonCombinationNode(fieldSchema);
          if (combinationKey.isPresent()) {
            var combinationCopy = dstCopy.get(key);
            final var arrayNode = (ArrayNode) fieldSchema.get(combinationKey.get());
            for (int i = 0; i < arrayNode.size(); i++) {
              final JsonNode childSchema = arrayNode.get(i);
              /*
               * when traversing a oneOf or anyOf if multiple schema in the oneOf or anyOf have the SAME key, but
               * a different type, then, without this test, we can try to apply the wrong schema to the object
               * resulting in errors because of type mismatches.
               */
              if (VALIDATOR.test(childSchema, combinationCopy)) {
                // Absorb field values if any of the combination option is declaring it as secrets
                combinationCopy = copySecrets(src.get(key), combinationCopy, childSchema);
              }
            }
            dstCopy.set(key, combinationCopy);
          } else {
            // Otherwise, this is just a plain old json node; recurse into it. If it's not actually an object,
            // the recursive call will exit immediately.
            final JsonNode copiedField = copySecrets(src.get(key), dstCopy.get(key), fieldSchema);
            dstCopy.set(key, copiedField);
          }
        }
      }

      return dstCopy;
    }

    return src;
  }

  static boolean isSecret(final JsonNode obj) {
    return obj.isObject() && obj.has(AIRBYTE_SECRET_FIELD) && obj.get(AIRBYTE_SECRET_FIELD).asBoolean();
  }

  protected JsonNode maskAllSecrets(final JsonNode obj, final SecretKeys secretKeys) {
    final JsonNode copiedObj = obj.deepCopy();
    final Queue<JsonNode> toProcess = new LinkedList<>();
    toProcess.add(copiedObj);

    while (!toProcess.isEmpty()) {
      final JsonNode currentNode = toProcess.remove();
      for (final String key : Jsons.keys(currentNode)) {
        if (secretKeys.fieldSecretKey.contains(key)) {
          ((ObjectNode) currentNode).put(key, SECRETS_MASK);
        } else if (currentNode.get(key).isObject()) {
          toProcess.add(currentNode.get(key));
        } else if (currentNode.get(key).isArray()) {
          if (secretKeys.arraySecretKey.contains(key)) {
            final ArrayNode sanitizedArrayNode = new ArrayNode(JsonNodeFactory.instance);
            currentNode.get(key).forEach((secret) -> sanitizedArrayNode.add(SECRETS_MASK));
            ((ObjectNode) currentNode).put(key, sanitizedArrayNode);
          } else {
            final ArrayNode arrayNode = (ArrayNode) currentNode.get(key);
            arrayNode.forEach((node) -> {
              toProcess.add(node);
            });
          }
        }
      }
    }

    return copiedObj;
  }

  @Value
  protected class SecretKeys {

    private final Set<String> fieldSecretKey;
    private final Set<String> arraySecretKey;

  }

  protected SecretKeys getAllSecretKeys(final JsonNode schema) {
    final Set<String> fieldSecretKeys = new HashSet<>();
    final Set<String> arraySecretKeys = new HashSet<>();

    final Queue<JsonNode> toProcess = new LinkedList<>();
    toProcess.add(schema);

    while (!toProcess.isEmpty()) {
      final JsonNode currentNode = toProcess.remove();
      for (final String key : Jsons.keys(currentNode)) {
        if (isArrayDefinition(currentNode.get(key))) {
          final JsonNode arrayItems = currentNode.get(key).get(ITEMS_FIELD);
          if (arrayItems.has(AIRBYTE_SECRET_FIELD) && arrayItems.get(AIRBYTE_SECRET_FIELD).asBoolean()) {
            arraySecretKeys.add(key);
          } else {
            toProcess.add(arrayItems);
          }
        } else if (JsonSecretsProcessor.isSecret(currentNode.get(key))) {
          fieldSecretKeys.add(key);
        } else if (currentNode.get(key).isObject()) {
          toProcess.add(currentNode.get(key));
        } else if (currentNode.get(key).isArray()) {
          final ArrayNode arrayNode = (ArrayNode) currentNode.get(key);
          arrayNode.forEach((node) -> {
            toProcess.add(node);
          });
        }
      }
    }

    return new SecretKeys(fieldSecretKeys, arraySecretKeys);
  }

  public static Optional<String> findJsonCombinationNode(final JsonNode node) {
    for (final String combinationNode : List.of("allOf", "anyOf", "oneOf")) {
      if (node.has(combinationNode) && node.get(combinationNode).isArray()) {
        return Optional.of(combinationNode);
      }
    }
    return Optional.empty();
  }

  public static boolean canBeProcessed(final JsonNode schema) {
    return schema.isObject() && schema.has(PROPERTIES_FIELD) && schema.get(PROPERTIES_FIELD).isObject();
  }

  public static boolean isArrayDefinition(final JsonNode obj) {
    return obj.isObject()
        && obj.has(TYPE_FIELD)
        && obj.get(TYPE_FIELD).asText().equals(ARRAY_TYPE_FIELD)
        && obj.has(ITEMS_FIELD);
  }

}

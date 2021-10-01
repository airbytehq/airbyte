/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JsonSecretsProcessor {

  public static String AIRBYTE_SECRET_FIELD = "airbyte_secret";
  public static final String PROPERTIES_FIELD = "properties";

  private static final Logger LOGGER = LoggerFactory.getLogger(JsonSecretsProcessor.class);

  @VisibleForTesting
  static String SECRETS_MASK = "**********";

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
  // todo: fix bug where this doesn't handle non-oneof nesting or just arrays
  // see: https://github.com/airbytehq/airbyte/issues/6393
  public JsonNode maskSecrets(JsonNode obj, JsonNode schema) {
    // if schema is an object and has a properties field
    if (!canBeProcessed(schema)) {
      return obj;
    }
    Preconditions.checkArgument(schema.isObject());
    // get the properties field
    ObjectNode properties = (ObjectNode) schema.get(PROPERTIES_FIELD);
    JsonNode copy = obj.deepCopy();
    // for the property keys
    for (String key : Jsons.keys(properties)) {
      JsonNode fieldSchema = properties.get(key);
      // if the json schema field is an obj and has the airbyte secret field
      if (isSecret(fieldSchema) && copy.has(key)) {
        // mask and set it
        if (copy.has(key)) {
          ((ObjectNode) copy).put(key, SECRETS_MASK);
        }
      }

      var combinationKey = findJsonCombinationNode(fieldSchema);
      if (combinationKey.isPresent() && copy.has(key)) {
        var combinationCopy = copy.get(key);
        var arrayNode = (ArrayNode) fieldSchema.get(combinationKey.get());
        for (int i = 0; i < arrayNode.size(); i++) {
          // Mask field values if any of the combination option is declaring it as secrets
          combinationCopy = maskSecrets(combinationCopy, arrayNode.get(i));
        }
        ((ObjectNode) copy).set(key, combinationCopy);
      }
    }

    return copy;
  }

  public static Optional<String> findJsonCombinationNode(JsonNode node) {
    for (String combinationNode : List.of("allOf", "anyOf", "oneOf")) {
      if (node.has(combinationNode) && node.get(combinationNode).isArray()) {
        return Optional.of(combinationNode);
      }
    }
    return Optional.empty();
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
  public JsonNode copySecrets(JsonNode src, JsonNode dst, JsonNode schema) {
    if (!canBeProcessed(schema)) {
      return dst;
    }
    Preconditions.checkArgument(dst.isObject());
    Preconditions.checkArgument(src.isObject());

    ObjectNode dstCopy = dst.deepCopy();

    ObjectNode properties = (ObjectNode) schema.get(PROPERTIES_FIELD);
    for (String key : Jsons.keys(properties)) {
      JsonNode fieldSchema = properties.get(key);
      // We only copy the original secret if the destination object isn't attempting to overwrite it
      // i.e: if the value of the secret isn't set to the mask
      if (isSecret(fieldSchema) && src.has(key)) {
        if (dst.has(key) && dst.get(key).asText().equals(SECRETS_MASK))
          dstCopy.set(key, src.get(key));
      }

      var combinationKey = findJsonCombinationNode(fieldSchema);
      if (combinationKey.isPresent() && dstCopy.has(key)) {
        var combinationCopy = dstCopy.get(key);
        if (src.has(key)) {
          var arrayNode = (ArrayNode) fieldSchema.get(combinationKey.get());
          for (int i = 0; i < arrayNode.size(); i++) {
            // Absorb field values if any of the combination option is declaring it as secrets
            combinationCopy = copySecrets(src.get(key), combinationCopy, arrayNode.get(i));
          }
        }
        dstCopy.set(key, combinationCopy);
      }
    }

    return dstCopy;
  }

  public static boolean isSecret(JsonNode obj) {
    return obj.isObject() && obj.has(AIRBYTE_SECRET_FIELD) && obj.get(AIRBYTE_SECRET_FIELD).asBoolean();
  }

  public static boolean canBeProcessed(JsonNode schema) {
    return schema.isObject() && schema.has(PROPERTIES_FIELD) && schema.get(PROPERTIES_FIELD).isObject();
  }

}

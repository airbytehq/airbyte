/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import lombok.Builder;

@Builder
public class JsonSecretsProcessorFactory {

  @Builder.Default
  private boolean maskSecrets = true;

  @Builder.Default
  private boolean copySecrets = true;

  public JsonSecretsProcessor createJsonSecretsProcessor() {
    return new JsonSecretsProcessor() {

      @Override
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

      @Override
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
                // Otherwise, this is just a plain old json node; recurse into it. If it's not actually an object, the recursive call will exit immediately.
                final JsonNode copiedField = copySecrets(src.get(key), dstCopy.get(key), fieldSchema);
                dstCopy.set(key, copiedField);
              }
            }
          }

          return dstCopy;
        }

        return src;
      }

    };
  }

}

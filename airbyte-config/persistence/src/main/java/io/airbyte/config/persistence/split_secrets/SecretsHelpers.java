/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import com.google.api.client.util.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.apache.commons.lang3.NotImplementedException;

public class SecretsHelpers {

  public static SplitSecretConfig split(Supplier<UUID> uuidSupplier, UUID workspaceId, JsonNode fullConfig, ConnectorSpecification spec) {
    return split(uuidSupplier, workspaceId, Jsons.emptyObject(), fullConfig, spec.getConnectionSpecification(), new NoOpSecretPersistence()::read);
  }

  private static SplitSecretConfig split(Supplier<UUID> uuidSupplier, UUID workspaceId, JsonNode old, JsonNode fullConfig, JsonNode spec, ReadOnlySecretPersistence roPersistence) {
    final var obj = fullConfig.deepCopy();
    final var schema = spec.deepCopy();
    final var secretMap = new HashMap<SecretCoordinate, String>();

    Preconditions.checkArgument(JsonSecretsProcessor.canBeProcessed(schema), "Schema is not valid JSONSchema!");

    // get the properties field
    ObjectNode properties = (ObjectNode) schema.get(JsonSecretsProcessor.PROPERTIES_FIELD);
    JsonNode copy = obj.deepCopy();
    // for the property keys
    for (String key : Jsons.keys(properties)) {
      JsonNode fieldSchema = properties.get(key);
      // if the json schema field is an obj and has the airbyte secret field
      if (JsonSecretsProcessor.isSecret(fieldSchema) && copy.has(key)) {
        // remove the key put the new key in the coordinate section
        Preconditions.checkArgument(copy.get(key).isTextual(), "Secrets must be strings!");
        final var newSecret = copy.get(key).asText();

        String coordinateBase = null;
        var version = 1L;
        if (old.has(key)) {
          final var oldSecret = old.get(key);

          if (oldSecret.has("_secret")) {
            var oldCoordinate = SecretCoordinate.fromFullCoordinate(oldSecret.get("_secret").asText());
            coordinateBase = oldCoordinate.getCoordinateBase();
            final var oldSecretValue = roPersistence.apply(oldCoordinate);
            System.out.println("111 oldSecretValue = " + oldSecretValue);
            if(oldSecretValue.isPresent()) {
              if(oldSecretValue.get().equals(newSecret)) {
                version = oldCoordinate.getVersion();
              } else {
                version = oldCoordinate.getVersion() + 1;
              }
            }
          }
        }

        if (coordinateBase == null) {
          coordinateBase = "airbyte_workspace_" + workspaceId + "_secret_" + uuidSupplier.get();
        }

        final var secretCoordinate = new SecretCoordinate(coordinateBase, version);

        secretMap.put(secretCoordinate, newSecret);
        System.out.println("secretCoordinate = " + secretCoordinate);
        System.out.println("newSecret = " + newSecret);
        ((ObjectNode) copy).replace(key, Jsons.jsonNode(Map.of("_secret", secretCoordinate.toString())));
      }

      var combinationKey = JsonSecretsProcessor.findJsonCombinationNode(fieldSchema);
      if (combinationKey.isPresent() && copy.has(key)) {
        var combinationCopy = copy.get(key);
        var arrayNode = (ArrayNode) fieldSchema.get(combinationKey.get());
        for (int i = 0; i < arrayNode.size(); i++) {
          final var newOld = old.has(key) ? old.get(key) : Jsons.emptyObject();
          final var combinationSplitConfig = split(uuidSupplier, workspaceId, newOld, combinationCopy, arrayNode.get(i), roPersistence);
          combinationCopy = combinationSplitConfig.getPartialConfig();
          secretMap.putAll(combinationSplitConfig.getCoordinateToPayload());
        }
        ((ObjectNode) copy).set(key, combinationCopy);
      } else if (fieldSchema.has("type") && fieldSchema.get("type").asText().equals("object") && fieldSchema.has("properties") && copy.has(key)) {
        final var newOld = old.has(key) ? old.get(key) : Jsons.emptyObject();
        final var nestedSplitConfig = split(uuidSupplier, workspaceId, newOld, copy.get(key), fieldSchema, roPersistence);
        ((ObjectNode) copy).replace(key, nestedSplitConfig.getPartialConfig());
        secretMap.putAll(nestedSplitConfig.getCoordinateToPayload());
      } else if (fieldSchema.has("type") && fieldSchema.get("type").asText().equals("array") && fieldSchema.has("items") && copy.has(key)) {
        final var itemType = fieldSchema.get("items").get("type");
        if (itemType == null) {
          throw new NotImplementedException();
        } else if (itemType.asText().equals("string") && fieldSchema.get("items").has("airbyte_secret")) {
          final var newOld = old.has(key) ? old.get(key) : Jsons.emptyObject();
          for (int i = 0; i < copy.get(key).size(); i++) {
            String coordinateBase = null;
            String newSecret = copy.get(key).get(i).asText();
            var version = 1L;
            if (newOld.has(i)) {
              final var oldSecret = newOld.get(i);

              if (oldSecret.has("_secret")) {
                var oldCoordinate = SecretCoordinate.fromFullCoordinate(oldSecret.get("_secret").asText());
                coordinateBase = oldCoordinate.getCoordinateBase();
                final var oldSecretValue = roPersistence.apply(oldCoordinate);
                if(oldSecretValue.isPresent()) {
                  if(oldSecretValue.get().equals(newSecret)) {
                    version = oldCoordinate.getVersion();
                  } else {
                    version = oldCoordinate.getVersion() + 1;
                  }
                }
              }
            }

            if (coordinateBase == null) {
              coordinateBase = "airbyte_workspace_" + workspaceId + "_secret_" + uuidSupplier.get();
            }

            final var secretCoordinate = new SecretCoordinate(coordinateBase, version);

            secretMap.put(secretCoordinate, newSecret);
            ((ArrayNode) copy.get(key)).set(i, Jsons.jsonNode(Map.of("_secret", secretCoordinate.toString())));
          }
        } else if (itemType.asText().equals("object")) {
          final var newOld = old.has(key) ? old.get(key) : Jsons.emptyObject();
          for (int i = 0; i < copy.get(key).size(); i++) {
            final var newOldElement = newOld.has(i) ? newOld.get(i) : Jsons.emptyObject();
            final var splitSecret = split(uuidSupplier, workspaceId, newOldElement, copy.get(key).get(i), fieldSchema.get("items"), roPersistence);
            secretMap.putAll(splitSecret.getCoordinateToPayload());
            ((ArrayNode) copy.get(key)).set(i, splitSecret.getPartialConfig());
          }
        }
      }
    }

    return new SplitSecretConfig(copy, secretMap);
  }

  public static SplitSecretConfig splitUpdate(Supplier<UUID> uuidSupplier,
                                              UUID workspaceId,
                                              JsonNode oldPartialConfig,
                                              JsonNode newFullConfig,
                                              ConnectorSpecification spec,
                                              ReadOnlySecretPersistence roPersistence) {
    return split(uuidSupplier, workspaceId, oldPartialConfig, newFullConfig, spec.getConnectionSpecification(), roPersistence);
  }

  public static JsonNode combine(JsonNode partialConfig, SecretPersistence secretPersistence) {
    return combine(true, partialConfig, secretPersistence);
  }

  private static JsonNode combine(boolean isFirst, JsonNode partialConfig, SecretPersistence secretPersistence) {
    final var config = isFirst ? partialConfig.deepCopy() : partialConfig;

    if (config.has("_secret")) {
      final var coordinate = SecretCoordinate.fromFullCoordinate(config.get("_secret").asText());
      return new TextNode(secretPersistence.read(coordinate).get());
    }

    config.fields().forEachRemaining(field -> {
      final var node = field.getValue();
      final var childFields = MoreStreams.toStream(node.fields()).collect(Collectors.toList());
      for (Map.Entry<String, JsonNode> childField : childFields) {
        final var childNode = childField.getValue();

        if (childField.getKey().equals("_secret")) {
          final var coordinate = SecretCoordinate.fromFullCoordinate(childNode.asText());
          final var secretValue = secretPersistence.read(coordinate);

          if(secretValue.isEmpty()) {
            throw new RuntimeException("That secret was not found in the store!");
          }

          ((ObjectNode) config).replace(field.getKey(), new TextNode(secretValue.get()));
          break;
        } else if (childNode.has("_secret")) {
          final var coordinate = SecretCoordinate.fromFullCoordinate(childNode.get("_secret").asText());
          final var secretValue = secretPersistence.read(coordinate);

          if(secretValue.isEmpty()) {
            throw new RuntimeException("That secret was not found in the store!");
          }

          ((ObjectNode) node).replace(childField.getKey(), new TextNode(secretValue.get()));
        }
      }

      if (node instanceof ArrayNode) {
        for (int i = 0; i < node.size(); i++) {
          ((ArrayNode) node).set(i, combine(false, node.get(i), secretPersistence));
        }
      } else if (node instanceof ObjectNode) {
        combine(false, node, secretPersistence);
      }
    });
    return config;
  }
}

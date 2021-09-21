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
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.apache.commons.lang3.NotImplementedException;

import javax.annotation.Nullable;

public class SecretsHelpers {
  public static final String CONFIG_SECRET_FIELD = "_secret";
  public static final String SPEC_SECRET_FIELD = JsonSecretsProcessor.AIRBYTE_SECRET_FIELD;

  public static SplitSecretConfig split(Supplier<UUID> uuidSupplier, UUID workspaceId, JsonNode fullConfig, ConnectorSpecification spec) {
    return split(uuidSupplier, workspaceId, Jsons.emptyObject(), fullConfig, spec.getConnectionSpecification(), new NoOpSecretPersistence()::read);
  }

  private static SplitSecretConfig split(Supplier<UUID> uuidSupplier, UUID workspaceId, JsonNode oldPartialConfig, JsonNode fullConfig, JsonNode spec, ReadOnlySecretPersistence roPersistence) {
    Preconditions.checkArgument(JsonSecretsProcessor.canBeProcessed(spec), "Schema is not valid JSONSchema!");

    final var secretMap = new HashMap<SecretCoordinate, String>();

    // get the properties field
    ObjectNode properties = (ObjectNode) spec.get(JsonSecretsProcessor.PROPERTIES_FIELD);
    JsonNode copy = fullConfig.deepCopy();
    // for the property keys
    for (String key : Jsons.keys(properties)) {
      JsonNode fieldSchema = properties.get(key);
      // if the json schema field is an obj and has the airbyte secret field
      if (JsonSecretsProcessor.isSecret(fieldSchema) && copy.has(key)) {
        // remove the key put the new key in the coordinate section
        Preconditions.checkArgument(copy.get(key).isTextual(), "Secrets must be strings!");
        final var newSecret = copy.get(key).asText();

        final var oldSecretFullCoordinate = getOldSecretFullCoordinate(oldPartialConfig, key);
        final var secretCoordinate = getCoordinate(
                newSecret,
                roPersistence,
                workspaceId,
                uuidSupplier,
                oldSecretFullCoordinate);

        secretMap.put(secretCoordinate, newSecret);
        ((ObjectNode) copy).replace(key, Jsons.jsonNode(Map.of(CONFIG_SECRET_FIELD, secretCoordinate.toString())));
      }

      var combinationKey = JsonSecretsProcessor.findJsonCombinationNode(fieldSchema);
      if (combinationKey.isPresent() && copy.has(key)) {
        var combinationCopy = copy.get(key);
        var arrayNode = (ArrayNode) fieldSchema.get(combinationKey.get());
        for (int i = 0; i < arrayNode.size(); i++) {
          final var newOld = oldPartialConfig.has(key) ? oldPartialConfig.get(key) : Jsons.emptyObject();
          final var combinationSplitConfig = split(uuidSupplier, workspaceId, newOld, combinationCopy, arrayNode.get(i), roPersistence);
          combinationCopy = combinationSplitConfig.getPartialConfig();
          secretMap.putAll(combinationSplitConfig.getCoordinateToPayload());
        }
        ((ObjectNode) copy).set(key, combinationCopy);
      } else if (fieldSchema.has("type") && fieldSchema.get("type").asText().equals("object") && fieldSchema.has("properties") && copy.has(key)) {
        final var newOld = oldPartialConfig.has(key) ? oldPartialConfig.get(key) : Jsons.emptyObject();
        final var nestedSplitConfig = split(uuidSupplier, workspaceId, newOld, copy.get(key), fieldSchema, roPersistence);
        ((ObjectNode) copy).replace(key, nestedSplitConfig.getPartialConfig());
        secretMap.putAll(nestedSplitConfig.getCoordinateToPayload());
      } else if (fieldSchema.has("type") && fieldSchema.get("type").asText().equals("array") && fieldSchema.has("items") && copy.has(key)) {
        final var itemType = fieldSchema.get("items").get("type");
        if (itemType == null) {
          throw new NotImplementedException();
        } else if (itemType.asText().equals("string") && fieldSchema.get("items").has(SPEC_SECRET_FIELD)) {
          final var newOld = oldPartialConfig.has(key) ? oldPartialConfig.get(key) : Jsons.emptyObject();
          for (int i = 0; i < copy.get(key).size(); i++) {
            String newSecret = copy.get(key).get(i).asText();

            final var oldSecretFullCoordinate = getOldSecretFullCoordinate(newOld, i);
            final var secretCoordinate = getCoordinate(
                    newSecret,
                    roPersistence,
                    workspaceId,
                    uuidSupplier,
                    oldSecretFullCoordinate);

            secretMap.put(secretCoordinate, newSecret);
            ((ArrayNode) copy.get(key)).set(i, Jsons.jsonNode(Map.of("_secret", secretCoordinate.toString())));
          }
        } else if (itemType.asText().equals("object")) {
          final var newOld = oldPartialConfig.has(key) ? oldPartialConfig.get(key) : Jsons.emptyObject();
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

    if (config.has(CONFIG_SECRET_FIELD)) {
      final var coordinate = SecretCoordinate.fromFullCoordinate(config.get(CONFIG_SECRET_FIELD).asText());
      return getOrThrowSecretValue(secretPersistence, coordinate);
    }

    config.fields().forEachRemaining(field -> {
      final var node = field.getValue();
      final var childFields = MoreStreams.toStream(node.fields()).collect(Collectors.toList());
      for (Map.Entry<String, JsonNode> childField : childFields) {
        final var childNode = childField.getValue();

        if (childField.getKey().equals(CONFIG_SECRET_FIELD)) {
          final var coordinate = SecretCoordinate.fromFullCoordinate(childNode.asText());
          ((ObjectNode) config).replace(field.getKey(), getOrThrowSecretValue(secretPersistence, coordinate));
          break;
        } else if (childNode.has(CONFIG_SECRET_FIELD)) {
          final var coordinate = SecretCoordinate.fromFullCoordinate(childNode.get(CONFIG_SECRET_FIELD).asText());
          ((ObjectNode) node).replace(childField.getKey(), getOrThrowSecretValue(secretPersistence, coordinate));
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

  private static TextNode getOrThrowSecretValue(SecretPersistence secretPersistence, SecretCoordinate coordinate) {
    final var secretValue = secretPersistence.read(coordinate);

    if(secretValue.isEmpty()) {
      throw new RuntimeException("That secret was not found in the store!");
    }

    return new TextNode(secretValue.get());
  }

  private static String getOldSecretFullCoordinate(
          final JsonNode oldNode,
          final String key) {
    if (oldNode.has(key) && oldNode.get(key).has(CONFIG_SECRET_FIELD)) {
      return oldNode.get(key).get(CONFIG_SECRET_FIELD).asText();
    } else {
      return null;
    }
  }

  private static String getOldSecretFullCoordinate(
          final JsonNode oldNode,
          final int key) {
    if (oldNode.has(key) && oldNode.get(key).has(CONFIG_SECRET_FIELD)) {
      return oldNode.get(key).get(CONFIG_SECRET_FIELD).asText();
    } else {
      return null;
    }
  }

  private static SecretCoordinate getCoordinate(
          final String newSecret,
          final ReadOnlySecretPersistence roPersistence,
          final UUID workspaceId,
          final Supplier<UUID> uuidSupplier,
          final @Nullable String oldSecretFullCoordinate) {
    String coordinateBase = null;
    Long version = null;

    if (oldSecretFullCoordinate != null) {
        var oldCoordinate = SecretCoordinate.fromFullCoordinate(oldSecretFullCoordinate);
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

    if (coordinateBase == null) {
      coordinateBase = "airbyte_workspace_" + workspaceId + "_secret_" + uuidSupplier.get();
    }

    if(version == null) {
      version = 1L;
    }

    return new SecretCoordinate(coordinateBase, version);
  }
}

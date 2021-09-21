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
import com.google.common.collect.Iterators;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.apache.commons.lang3.NotImplementedException;

import javax.annotation.Nullable;

public class SecretsHelpers {
  public static final String COORDINATE_FIELD = "_secret";
  public static final String SPEC_SECRET_FIELD = JsonSecretsProcessor.AIRBYTE_SECRET_FIELD;

  public static SplitSecretConfig split(
          final Supplier<UUID> uuidSupplier,
          final UUID workspaceId,
          final JsonNode fullConfig,
          final ConnectorSpecification spec) {
    return split(uuidSupplier, workspaceId, Jsons.emptyObject(), fullConfig, spec.getConnectionSpecification(), new NoOpSecretPersistence()::read);
  }

  public static SplitSecretConfig splitUpdate(final Supplier<UUID> uuidSupplier,
                                              final UUID workspaceId,
                                              final JsonNode oldPartialConfig,
                                              final JsonNode newFullConfig,
                                              final ConnectorSpecification spec,
                                              final ReadOnlySecretPersistence secretReader) {
    return split(uuidSupplier, workspaceId, oldPartialConfig, newFullConfig, spec.getConnectionSpecification(), secretReader);
  }


  public static JsonNode combine(final JsonNode partialConfig, final SecretPersistence secretPersistence) {
    final var config = partialConfig.deepCopy();

    // if the entire config is a secret coordinate object
    if (config.has(COORDINATE_FIELD)) {
      final var coordinateNode = config.get(COORDINATE_FIELD);
      final var coordinate = getCoordinateFromTextNode(coordinateNode);
      return getOrThrowSecretValueNode(secretPersistence, coordinate);
    }

    // otherwise iterate through all object fields
    config.fields().forEachRemaining(field -> {
      final var fieldName = field.getKey();
      final var fieldNode = field.getValue();

      if (fieldNode instanceof ArrayNode) {
        for (int i = 0; i < fieldNode.size(); i++) {
          ((ArrayNode) fieldNode).set(i, combine(fieldNode.get(i), secretPersistence));
        }
      } else if (fieldNode instanceof ObjectNode) {
        ((ObjectNode) config).replace(fieldName, combine(fieldNode, secretPersistence));
      }
    });

    return config;
  }

  private static SplitSecretConfig split(
          final Supplier<UUID> uuidSupplier,
          final UUID workspaceId,
          final JsonNode oldPartialConfig,
          final JsonNode originalFullConfig,
          final JsonNode spec,
          final ReadOnlySecretPersistence secretReader) {
    Preconditions.checkArgument(JsonSecretsProcessor.canBeProcessed(spec), "Schema is not valid JSONSchema!");

    final var fullConfig = originalFullConfig.deepCopy();
    final var secretMap = new HashMap<SecretCoordinate, String>();
    final var specProperties = (ObjectNode) spec.get(JsonSecretsProcessor.PROPERTIES_FIELD);

    for (String specProperty : Jsons.keys(specProperties)) {
      final var fieldSchema = specProperties.get(specProperty);
      final var fieldSchemaCombinationType = JsonSecretsProcessor.findJsonCombinationNode(fieldSchema);

      // if the json schema field is an obj and has the airbyte secret field
      if (JsonSecretsProcessor.isSecret(fieldSchema) && fullConfig.has(specProperty)) {
        // remove the key put the new key in the coordinate section
        Preconditions.checkArgument(fullConfig.get(specProperty).isTextual(), "Secrets must be strings!");
        final var newSecret = fullConfig.get(specProperty).asText();

        final var oldSecretFullCoordinate = getCoordinateFromObjectNode(oldPartialConfig, specProperty);
        final var secretCoordinate = getCoordinate(newSecret, secretReader, workspaceId, uuidSupplier, oldSecretFullCoordinate);

        secretMap.put(secretCoordinate, newSecret);
        ((ObjectNode) fullConfig).replace(specProperty, Jsons.jsonNode(Map.of(COORDINATE_FIELD, secretCoordinate.toString())));
      } else if (fieldSchemaCombinationType.isPresent() && fullConfig.has(specProperty)) {
        var combinationCopy = fullConfig.get(specProperty);
        var arrayNode = (ArrayNode) fieldSchema.get(fieldSchemaCombinationType.get());
        for (int i = 0; i < arrayNode.size(); i++) {
          final var newOld = oldPartialConfig.has(specProperty) ? oldPartialConfig.get(specProperty) : Jsons.emptyObject();
          final var combinationSplitConfig = split(uuidSupplier, workspaceId, newOld, combinationCopy, arrayNode.get(i), secretReader);
          combinationCopy = combinationSplitConfig.getPartialConfig();
          secretMap.putAll(combinationSplitConfig.getCoordinateToPayload());
        }
        ((ObjectNode) fullConfig).set(specProperty, combinationCopy);
      } else if (fieldSchema.has("type") && fieldSchema.get("type").asText().equals("object") && fieldSchema.has("properties") && fullConfig.has(specProperty)) {
        final var newOld = oldPartialConfig.has(specProperty) ? oldPartialConfig.get(specProperty) : Jsons.emptyObject();
        final var nestedSplitConfig = split(uuidSupplier, workspaceId, newOld, fullConfig.get(specProperty), fieldSchema, secretReader);
        ((ObjectNode) fullConfig).replace(specProperty, nestedSplitConfig.getPartialConfig());
        secretMap.putAll(nestedSplitConfig.getCoordinateToPayload());
      } else if (fieldSchema.has("type") && fieldSchema.get("type").asText().equals("array") && fieldSchema.has("items") && fullConfig.has(specProperty)) {
        final var itemType = fieldSchema.get("items").get("type");
        if (itemType == null) {
          throw new NotImplementedException();
        } else if (itemType.asText().equals("string") && fieldSchema.get("items").has(SPEC_SECRET_FIELD)) {
          final var newOld = oldPartialConfig.has(specProperty) ? oldPartialConfig.get(specProperty) : Jsons.emptyObject();
          for (int i = 0; i < fullConfig.get(specProperty).size(); i++) {
            String newSecret = fullConfig.get(specProperty).get(i).asText();

            final var oldSecretFullCoordinate = getCoordinateFromObjectNode(newOld, i);
            final var secretCoordinate = getCoordinate(newSecret, secretReader, workspaceId, uuidSupplier, oldSecretFullCoordinate);

            secretMap.put(secretCoordinate, newSecret);
            ((ArrayNode) fullConfig.get(specProperty)).set(i, Jsons.jsonNode(Map.of("_secret", secretCoordinate.toString())));
          }
        } else if (itemType.asText().equals("object")) {
          final var newOld = oldPartialConfig.has(specProperty) ? oldPartialConfig.get(specProperty) : Jsons.emptyObject();
          for (int i = 0; i < fullConfig.get(specProperty).size(); i++) {
            final var newOldElement = newOld.has(i) ? newOld.get(i) : Jsons.emptyObject();
            final var splitSecret = split(uuidSupplier, workspaceId, newOldElement, fullConfig.get(specProperty).get(i), fieldSchema.get("items"), secretReader);
            secretMap.putAll(splitSecret.getCoordinateToPayload());
            ((ArrayNode) fullConfig.get(specProperty)).set(i, splitSecret.getPartialConfig());
          }
        }
      }
    }

    return new SplitSecretConfig(fullConfig, secretMap);
  }

  private static TextNode getOrThrowSecretValueNode(final SecretPersistence secretPersistence, final SecretCoordinate coordinate) {
    final var secretValue = secretPersistence.read(coordinate);

    if(secretValue.isEmpty()) {
      throw new RuntimeException("That secret was not found in the store!");
    }

    return new TextNode(secretValue.get());
  }

  private static SecretCoordinate getCoordinateFromTextNode(JsonNode node) {
    return SecretCoordinate.fromFullCoordinate(node.asText());
  }

  private static String getCoordinateFromObjectNode(
          final JsonNode node,
          final String key) {
    if (node.has(key) && node.get(key).has(COORDINATE_FIELD)) {
      return node.get(key).get(COORDINATE_FIELD).asText();
    } else {
      return null;
    }
  }

  private static String getCoordinateFromObjectNode(
          final JsonNode node,
          final int key) {
    if (node.has(key) && node.get(key).has(COORDINATE_FIELD)) {
      return node.get(key).get(COORDINATE_FIELD).asText();
    } else {
      return null;
    }
  }

  private static SecretCoordinate getCoordinate(
          final String newSecret,
          final ReadOnlySecretPersistence secretReader,
          final UUID workspaceId,
          final Supplier<UUID> uuidSupplier,
          final @Nullable String oldSecretFullCoordinate) {
    String coordinateBase = null;
    Long version = null;

    if (oldSecretFullCoordinate != null) {
        var oldCoordinate = SecretCoordinate.fromFullCoordinate(oldSecretFullCoordinate);
        coordinateBase = oldCoordinate.getCoordinateBase();
        final var oldSecretValue = secretReader.apply(oldCoordinate);
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

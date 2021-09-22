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
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import javax.annotation.Nullable;
import org.apache.commons.lang3.NotImplementedException;

public class SecretsHelpers {

  public static final String COORDINATE_FIELD = "_secret";
  public static final String SPEC_SECRET_FIELD = JsonSecretsProcessor.AIRBYTE_SECRET_FIELD;

  public static SplitSecretConfig split(final Supplier<UUID> uuidSupplier,
                                        final UUID workspaceId,
                                        final JsonNode fullConfig,
                                        final ConnectorSpecification spec) {
    return split(uuidSupplier, workspaceId, new NoOpSecretPersistence()::read, Jsons.emptyObject(), fullConfig, spec.getConnectionSpecification());
  }

  public static SplitSecretConfig splitUpdate(final Supplier<UUID> uuidSupplier,
                                              final UUID workspaceId,
                                              final JsonNode oldPartialConfig,
                                              final JsonNode newFullConfig,
                                              final ConnectorSpecification spec,
                                              final ReadOnlySecretPersistence secretReader) {
    return split(uuidSupplier, workspaceId, secretReader, oldPartialConfig, newFullConfig, spec.getConnectionSpecification());
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

  private static SplitSecretConfig split(final Supplier<UUID> uuidSupplier,
                                         final UUID workspaceId,
                                         final ReadOnlySecretPersistence secretReader,
                                         final JsonNode oldPartialConfig,
                                         final JsonNode originalFullConfig,
                                         final JsonNode spec) {
    Preconditions.checkArgument(spec.has("type"), "Spec is not valid JSONSchema!");

    final var fullConfig = originalFullConfig.deepCopy();
    final var secretMap = new HashMap<SecretCoordinate, String>();

    // provide a lambda for hiding repeated arguments to improve readability
    final InternalSplitter splitter = (final JsonNode partialConfig, final JsonNode newFullConfig, final JsonNode newFullConfigSpec)
            -> split(uuidSupplier, workspaceId, secretReader, partialConfig, newFullConfig, newFullConfigSpec);

    if (isSecretSpecNode(spec)) {
      // if the input config is specified as a text node containing a secret, we make a secret coordinate object
      final var oldFullSecretCoordinate = oldPartialConfig.has(COORDINATE_FIELD) ? oldPartialConfig.get(COORDINATE_FIELD).asText() : null;
      final var secretCoordinate = getCoordinate(fullConfig.asText(), secretReader, workspaceId, uuidSupplier, oldFullSecretCoordinate);

      final var newPartialConfig = Jsons.jsonNode(Map.of(
          COORDINATE_FIELD, secretCoordinate.toString()));

      final var coordinateToPayload = Map.of(
          secretCoordinate,
          fullConfig.asText());

      return new SplitSecretConfig(newPartialConfig, coordinateToPayload);
    } else if (isObjectSchema(spec)) {
      final var specProperties = (ObjectNode) spec.get(JsonSecretsProcessor.PROPERTIES_FIELD);

      // if the input config is specified as an object, we go through and handle each type of property
      for (final String specProperty : Jsons.keys(specProperties)) {
        final var fieldSchema = specProperties.get(specProperty);
        final var fieldSchemaCombinationType = JsonSecretsProcessor.findJsonCombinationNode(fieldSchema);
        final var isCombinationNodeSchema = fieldSchemaCombinationType.isPresent();

      
        if (fullConfig.has(specProperty)) {
          final var nextOldPartialConfig = getFieldOrEmptyNode(oldPartialConfig, specProperty);
          if (JsonSecretsProcessor.isSecret(fieldSchema)) {
            final var splitConfig = splitter.split(nextOldPartialConfig, fullConfig.get(specProperty), fieldSchema);
            secretMap.putAll(splitConfig.getCoordinateToPayload());
            ((ObjectNode) fullConfig).replace(specProperty, splitConfig.getPartialConfig());
          } else if (isCombinationNodeSchema) {
            var combinationCopy = fullConfig.get(specProperty);
            final var arrayNode = (ArrayNode) fieldSchema.get(fieldSchemaCombinationType.get());
            for (int i = 0; i < arrayNode.size(); i++) {
              final var splitConfig = splitter.split(nextOldPartialConfig, combinationCopy, arrayNode.get(i));
              combinationCopy = splitConfig.getPartialConfig();
              secretMap.putAll(splitConfig.getCoordinateToPayload());
            }
            ((ObjectNode) fullConfig).set(specProperty, combinationCopy);
          } else if (isObjectSchema(fieldSchema)) {
            final var nestedSplitConfig = splitter.split(nextOldPartialConfig, fullConfig.get(specProperty), fieldSchema);
            ((ObjectNode) fullConfig).replace(specProperty, nestedSplitConfig.getPartialConfig());
            secretMap.putAll(nestedSplitConfig.getCoordinateToPayload());
          } else if (isArraySchema(fieldSchema)) {
            for (int i = 0; i < fullConfig.get(specProperty).size(); i++) {
              final var partialConfigElement = getFieldOrEmptyNode(nextOldPartialConfig, i);
              final var fullConfigElement = fullConfig.get(specProperty).get(i);
              final var splitConfig = splitter.split(partialConfigElement, fullConfigElement, fieldSchema.get("items"));
              secretMap.putAll(splitConfig.getCoordinateToPayload());
              ((ArrayNode) fullConfig.get(specProperty)).set(i, splitConfig.getPartialConfig());
            }
          }
        }
      }
    } else {
      throw new NotImplementedException("unexpected node type at this level!");
    }

    return new SplitSecretConfig(fullConfig, secretMap);
  }

  @FunctionalInterface
  public interface InternalSplitter {
    SplitSecretConfig split(JsonNode oldPartialConfig, JsonNode fullConfig, JsonNode spec);
  }

  private static boolean isSecretSpecNode(JsonNode spec) {
    return spec.get("type").asText().equals("string") && spec.has(SPEC_SECRET_FIELD) && spec.get(SPEC_SECRET_FIELD).asBoolean();
  }

  private static boolean isObjectSchema(JsonNode schema) {
    return schema.has("type") && schema.get("type").asText().equals("object") && schema.has("properties");
  }

  private static boolean isArraySchema(JsonNode schema) {
    return schema.has("type") && schema.get("type").asText().equals("array") && schema.has("items");
  }

  private static JsonNode getFieldOrEmptyNode(final JsonNode node, final String field) {
    return node.has(field) ? node.get(field) : Jsons.emptyObject();
  }

  private static JsonNode getFieldOrEmptyNode(final JsonNode node, final int field) {
    return node.has(field) ? node.get(field) : Jsons.emptyObject();
  }

  private static TextNode getOrThrowSecretValueNode(final SecretPersistence secretPersistence, final SecretCoordinate coordinate) {
    final var secretValue = secretPersistence.read(coordinate);

    if (secretValue.isEmpty()) {
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
      if (oldSecretValue.isPresent()) {
        if (oldSecretValue.get().equals(newSecret)) {
          version = oldCoordinate.getVersion();
        } else {
          version = oldCoordinate.getVersion() + 1;
        }
      }
    }

    if (coordinateBase == null) {
      coordinateBase = "airbyte_workspace_" + workspaceId + "_secret_" + uuidSupplier.get();
    }

    if (version == null) {
      version = 1L;
    }

    return new SecretCoordinate(coordinateBase, version);
  }

}

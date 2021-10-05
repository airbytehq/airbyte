/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import javax.annotation.Nullable;

/**
 * Contains most of the core logic surrounding secret coordinate extraction and insertion.
 *
 * These are the three main helpers provided by this class:
 * {@link SecretsHelpers#splitConfig(UUID, JsonNode, ConnectorSpecification)}
 * {@link SecretsHelpers#splitAndUpdateConfig(UUID, JsonNode, JsonNode, ConnectorSpecification, ReadOnlySecretPersistence)}
 * {@link SecretsHelpers#combineConfig(JsonNode, ReadOnlySecretPersistence)}
 *
 * Here's an overview on some terminology used in this class:
 *
 * A "full config" represents an entire connector config as specified by an end user. This should
 * conform to a connector specification.
 *
 * A "partial config" represents a connector config where any string that was specified as an
 * airbyte_secret in the connector specification is replaced by a JSON object {"_secret": "secret
 * coordinate"} that can later be used to reconstruct the "full config".
 *
 * A {@link SecretPersistence} provides the ability to read and write secrets to a backing store
 * such as Google Secrets Manager.
 *
 * A {@link SecretCoordinate} is a reference to a specific secret at a specific version in a
 * {@link SecretPersistence}.
 */
public class SecretsHelpers {

  public static final String COORDINATE_FIELD = "_secret";

  /**
   * Used to separate secrets out of a connector configuration. This will output a partial config that
   * includes pointers to secrets instead of actual secret values and a map that can be used to update
   * a {@link SecretPersistence} at coordinates with values from the full config.
   *
   * @param workspaceId workspace used for this connector config
   * @param fullConfig config including secrets
   * @param spec connector specification
   * @return a partial config + a map of coordinates to secret payloads
   */
  public static SplitSecretConfig splitConfig(final UUID workspaceId,
                                              final JsonNode fullConfig,
                                              final ConnectorSpecification spec) {
    return internalSplitAndUpdateConfig(UUID::randomUUID, workspaceId, (coordinate) -> Optional.empty(), Jsons.emptyObject(), fullConfig,
        spec.getConnectionSpecification());
  }

  /**
   * Used to separate secrets out of a connector configuration and output a partial config that
   * includes pointers to secrets instead of actual secret values and a map that can be used to update
   * a {@link SecretPersistence} at coordinates with values from the full config. If a previous config
   * for this connector's configuration is provided, this method attempts to use the same base
   * coordinates to refer to the same secret and increment the version of the coordinate used to
   * reference a secret.
   *
   * @param workspaceId workspace used for this connector config
   * @param oldPartialConfig previous partial config for this specific connector configuration
   * @param newFullConfig new config containing secrets that will be used to update the partial config
   *        for this connector
   * @param spec connector specification that should match both the previous partial config after
   *        filling in coordinates and the new full config.
   * @param secretReader provides a way to determine if a secret is the same or updated at a specific
   *        location in a config
   * @return a partial config + a map of coordinates to secret payloads
   */
  public static SplitSecretConfig splitAndUpdateConfig(final UUID workspaceId,
                                                       final JsonNode oldPartialConfig,
                                                       final JsonNode newFullConfig,
                                                       final ConnectorSpecification spec,
                                                       final ReadOnlySecretPersistence secretReader) {
    return internalSplitAndUpdateConfig(UUID::randomUUID, workspaceId, secretReader, oldPartialConfig, newFullConfig,
        spec.getConnectionSpecification());
  }

  /**
   * Replaces {"_secret": "full_coordinate"} objects in the partial config with the string secret
   * payloads loaded from the secret persistence at those coordinates.
   *
   * @param partialConfig configuration containing secret coordinates (references to secrets)
   * @param secretPersistence secret storage mechanism
   * @return full config including actual secret values
   */
  public static JsonNode combineConfig(final JsonNode partialConfig, final ReadOnlySecretPersistence secretPersistence) {
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
          ((ArrayNode) fieldNode).set(i, combineConfig(fieldNode.get(i), secretPersistence));
        }
      } else if (fieldNode instanceof ObjectNode) {
        ((ObjectNode) config).replace(fieldName, combineConfig(fieldNode, secretPersistence));
      }
    });

    return config;
  }

  /**
   * @param uuidSupplier provided to allow a test case to produce known UUIDs in order for easy
   *        fixture creation.
   */
  @VisibleForTesting
  public static SplitSecretConfig splitConfig(final Supplier<UUID> uuidSupplier,
                                              final UUID workspaceId,
                                              final JsonNode fullConfig,
                                              final ConnectorSpecification spec) {
    return internalSplitAndUpdateConfig(uuidSupplier, workspaceId, (coordinate) -> Optional.empty(), Jsons.emptyObject(), fullConfig,
        spec.getConnectionSpecification());
  }

  /**
   * @param uuidSupplier provided to allow a test case to produce known UUIDs in order for easy
   *        fixture creation.
   */
  @VisibleForTesting
  public static SplitSecretConfig splitAndUpdateConfig(final Supplier<UUID> uuidSupplier,
                                                       final UUID workspaceId,
                                                       final JsonNode oldPartialConfig,
                                                       final JsonNode newFullConfig,
                                                       final ConnectorSpecification spec,
                                                       final ReadOnlySecretPersistence secretReader) {
    return internalSplitAndUpdateConfig(uuidSupplier, workspaceId, secretReader, oldPartialConfig, newFullConfig, spec.getConnectionSpecification());
  }

  /**
   * Internal method used to support both "split config" and "split and update config" operations.
   *
   * For splits that don't have a prior partial config (such as when a connector is created for a
   * source or destination for the first time), the secret reader and old partial config can be set to
   * empty (see {@link SecretsHelpers#splitConfig(UUID, JsonNode, ConnectorSpecification)}).
   *
   * IMPORTANT: This is used recursively. In the process, the partial config, full config, and spec
   * inputs will represent internal json structures, not the entire configs/specs.
   *
   * @param uuidSupplier provided to allow a test case to produce known UUIDs in order for easy
   *        fixture creation
   * @param workspaceId workspace that will contain the source or destination this config will be
   *        stored for
   * @param secretReader provides a way to determine if a secret is the same or updated at a specific
   *        location in a config
   * @param oldPartialConfig previous partial config for this specific connector configuration
   * @param originalFullConfig new config containing secrets that will be used to update the partial
   *        config for this connector
   * @param spec connector specification
   * @return a partial config + a map of coordinates to secret payloads
   */
  private static SplitSecretConfig internalSplitAndUpdateConfig(final Supplier<UUID> uuidSupplier,
                                                                final UUID workspaceId,
                                                                final ReadOnlySecretPersistence secretReader,
                                                                final JsonNode oldPartialConfig,
                                                                final JsonNode originalFullConfig,
                                                                final JsonNode spec) {
    final var fullConfig = originalFullConfig.deepCopy();
    final var secretMap = new HashMap<SecretCoordinate, String>();

    // provide a lambda for hiding repeated arguments to improve readability
    final InternalSplitter splitter =
        (final JsonNode partialConfig, final JsonNode newFullConfig, final JsonNode newFullConfigSpec) -> internalSplitAndUpdateConfig(uuidSupplier,
            workspaceId,
            secretReader, partialConfig, newFullConfig, newFullConfigSpec);

    final var specTypeToHandle = getSpecTypeToHandle(spec);

    switch (specTypeToHandle) {
      case STRING -> {
        if (JsonSecretsProcessor.isSecret(spec)) {
          final var oldFullSecretCoordinate = oldPartialConfig.has(COORDINATE_FIELD) ? oldPartialConfig.get(COORDINATE_FIELD).asText() : null;
          final var secretCoordinate = getCoordinate(fullConfig.asText(), secretReader, workspaceId, uuidSupplier, oldFullSecretCoordinate);

          final var newPartialConfig = Jsons.jsonNode(Map.of(
              COORDINATE_FIELD, secretCoordinate.getFullCoordinate()));

          final var coordinateToPayload = Map.of(
              secretCoordinate,
              fullConfig.asText());

          return new SplitSecretConfig(newPartialConfig, coordinateToPayload);
        }
      }
      case OBJECT -> {
        final var specPropertiesObject = (ObjectNode) spec.get(JsonSecretsProcessor.PROPERTIES_FIELD);
        final var specProperties = Jsons.keys(specPropertiesObject).stream()
            .filter(fullConfig::has)
            .collect(Collectors.toList());

        // if the input config is specified as an object, we go through and handle each type of property
        for (final String specProperty : specProperties) {
          final var nextOldPartialConfig = getFieldOrEmptyNode(oldPartialConfig, specProperty);

          final var nestedSplitConfig =
              splitter.splitAndUpdateConfig(nextOldPartialConfig, fullConfig.get(specProperty), spec.get("properties").get(specProperty));
          ((ObjectNode) fullConfig).replace(specProperty, nestedSplitConfig.getPartialConfig());
          secretMap.putAll(nestedSplitConfig.getCoordinateToPayload());
        }
      }
      case ARRAY -> {
        for (int i = 0; i < fullConfig.size(); i++) {
          final var partialConfigElement = getFieldOrEmptyNode(oldPartialConfig, i);
          final var fullConfigElement = fullConfig.get(i);
          final var splitConfig = splitter.splitAndUpdateConfig(partialConfigElement, fullConfigElement, spec.get("items"));
          secretMap.putAll(splitConfig.getCoordinateToPayload());
          ((ArrayNode) fullConfig).set(i, splitConfig.getPartialConfig());
        }
      }
      case ONE_OF -> {
        final var possibleSchemas = (ArrayNode) spec.get("oneOf");

        for (int i = 0; i < possibleSchemas.size(); i++) {
          final var possibleSchema = possibleSchemas.get(i);
          final var set = new JsonSchemaValidator().validate(possibleSchema, fullConfig);
          if (set.isEmpty()) {
            final var splitConfig = splitter.splitAndUpdateConfig(oldPartialConfig, fullConfig, possibleSchema);
            if (!splitConfig.getPartialConfig().equals(fullConfig)) {
              return splitConfig;
            }
          }
        }
      }
    }

    return new SplitSecretConfig(fullConfig, secretMap);
  }

  /**
   * Enum that allows us to switch on different types seen in a config / spec.
   *
   * Unrecognized types refers to values that cannot contain string airbyte_secret secrets such as
   * numbers, binary fields, etc. They also may contain allOf or other mechanisms that aren't fully
   * supported in Airbyte connector configurations.
   */
  private enum JsonSchemaSpecType {
    OBJECT,
    ARRAY,
    STRING,
    ONE_OF,
    UNRECOGNIZED_TYPE
  }

  /**
   * Determines what the spec is referring to.
   *
   * @param spec connector specification or a sub-node of the specification
   * @return a type used to process a config or sub-node of a config
   */
  private static JsonSchemaSpecType getSpecTypeToHandle(JsonNode spec) {
    if (isObjectSchema(spec)) {
      return JsonSchemaSpecType.OBJECT;
    } else if (isArraySchema(spec)) {
      return JsonSchemaSpecType.ARRAY;
    } else if (isStringSchema(spec)) {
      return JsonSchemaSpecType.STRING;
    } else if (spec.has("oneOf") && spec.get("oneOf").isArray()) {
      return JsonSchemaSpecType.ONE_OF;
    } else {
      return JsonSchemaSpecType.UNRECOGNIZED_TYPE;
    }
  }

  /**
   * Interface used to make calls to
   * {@link SecretsHelpers#internalSplitAndUpdateConfig(Supplier, UUID, ReadOnlySecretPersistence, JsonNode, JsonNode, JsonNode)}
   * more readable by arguments that are the same across the entire method.
   */
  @FunctionalInterface
  public interface InternalSplitter {

    SplitSecretConfig splitAndUpdateConfig(JsonNode oldPartialConfig, JsonNode fullConfig, JsonNode spec);

  }

  private static boolean isStringSchema(JsonNode schema) {
    return schema.has("type") && schema.get("type").asText().equals("string");
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

  /**
   * Extracts a secret value from the persistence and throws an exception if the secret is not
   * available.
   *
   * @param secretPersistence storage layer for secrets
   * @param coordinate reference to a secret in the persistence
   * @throws RuntimeException when a secret at that coordinate is not available in the persistence
   * @return a json text node containing the secret value
   */
  private static TextNode getOrThrowSecretValueNode(final ReadOnlySecretPersistence secretPersistence, final SecretCoordinate coordinate) {
    final var secretValue = secretPersistence.read(coordinate);

    if (secretValue.isEmpty()) {
      throw new RuntimeException("That secret was not found in the store!");
    }

    return new TextNode(secretValue.get());
  }

  private static SecretCoordinate getCoordinateFromTextNode(JsonNode node) {
    return SecretCoordinate.fromFullCoordinate(node.asText());
  }

  /**
   * Determines which coordinate base and version to use based off of an old version that may exist in
   * the secret persistence.
   *
   * If the secret does not exist in the persistence, version 1 will be used.
   *
   * If the new secret value is the same as the old version stored in the persistence, the returned
   * coordinate will be the same as the previous version.
   *
   * If the new secret value is different from the old version stored in the persistence, the returned
   * coordinate will increase the version.
   *
   * @param newSecret new value of a secret provides a way to determine if a secret is the same or
   *        updated at a specific location in a config
   * @param workspaceId workspace used for this connector config
   * @param uuidSupplier provided to allow a test case to produce known UUIDs in order for easy
   *        fixture creation.
   * @param oldSecretFullCoordinate a nullable full coordinate (base+version) retrieved from the
   *        previous config
   * @return a coordinate (versioned reference to where the secret is stored in the persistence)
   */
  protected static SecretCoordinate getCoordinate(
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
      final var oldSecretValue = secretReader.read(oldCoordinate);
      if (oldSecretValue.isPresent()) {
        if (oldSecretValue.get().equals(newSecret)) {
          version = oldCoordinate.getVersion();
        } else {
          version = oldCoordinate.getVersion() + 1;
        }
      }
    }

    if (coordinateBase == null) {
      // IMPORTANT: format of this cannot be changed without introducing migrations for secrets
      // persistences
      coordinateBase = "airbyte_workspace_" + workspaceId + "_secret_" + uuidSupplier.get();
    }

    if (version == null) {
      version = 1L;
    }

    return new SecretCoordinate(coordinateBase, version);
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.constants.AirbyteSecretConstants;
import io.airbyte.commons.json.JsonPaths;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import javax.annotation.Nullable;

/**
 * Contains most of the core logic surrounding secret coordinate extraction and insertion.
 *
 * These are the three main helpers provided by this class:
 * {@link SecretsHelpers#splitConfig(UUID, JsonNode, JsonNode)}
 * {@link SecretsHelpers#splitAndUpdateConfig(UUID, JsonNode, JsonNode, JsonNode, ReadOnlySecretPersistence)}
 * {@link SecretsHelpers#combineConfig(JsonNode, ReadOnlySecretPersistence)}
 *
 * Here's an overview on some terminology used in this class:
 *
 * A "full config" represents an entire config as specified by an end user.
 *
 * A "partial config" represents a config where any string that was specified as an airbyte_secret
 * in the specification is replaced by a JSON object {"_secret": "secret coordinate"} that can later
 * be used to reconstruct the "full config".
 *
 * A {@link SecretPersistence} provides the ability to read and write secrets to a backing store
 * such as Google Secrets Manager.
 *
 * A {@link SecretCoordinate} is a reference to a specific secret at a specific version in a
 * {@link SecretPersistence}.
 */
@SuppressWarnings("PMD.AvoidThrowingRawExceptionTypes")
public class SecretsHelpers {

  public static final String COORDINATE_FIELD = "_secret";

  /**
   * Used to separate secrets out of some configuration. This will output a partial config that
   * includes pointers to secrets instead of actual secret values and a map that can be used to update
   * a {@link SecretPersistence} at coordinates with values from the full config.
   *
   * @param workspaceId workspace used for this config
   * @param fullConfig config including secrets
   * @param spec specification for the config
   * @return a partial config + a map of coordinates to secret payloads
   */
  public static SplitSecretConfig splitConfig(final UUID workspaceId,
                                              final JsonNode fullConfig,
                                              final JsonNode spec) {
    return internalSplitAndUpdateConfig(
        UUID::randomUUID,
        workspaceId,
        (coordinate) -> Optional.empty(),
        Jsons.emptyObject(),
        fullConfig,
        spec);
  }

  /**
   * Used to separate secrets out of a configuration and output a partial config that includes
   * pointers to secrets instead of actual secret values and a map that can be used to update a
   * {@link SecretPersistence} at coordinates with values from the full config. If a previous config
   * for this configuration is provided, this method attempts to use the same base coordinates to
   * refer to the same secret and increment the version of the coordinate used to reference a secret.
   *
   * @param workspaceId workspace used for this config
   * @param oldPartialConfig previous partial config for this specific configuration
   * @param newFullConfig new config containing secrets that will be used to update the partial config
   * @param spec specification that should match both the previous partial config after filling in
   *        coordinates and the new full config.
   * @param secretReader provides a way to determine if a secret is the same or updated at a specific
   *        location in a config
   * @return a partial config + a map of coordinates to secret payloads
   */
  public static SplitSecretConfig splitAndUpdateConfig(final UUID workspaceId,
                                                       final JsonNode oldPartialConfig,
                                                       final JsonNode newFullConfig,
                                                       final JsonNode spec,
                                                       final ReadOnlySecretPersistence secretReader) {
    return internalSplitAndUpdateConfig(
        UUID::randomUUID,
        workspaceId,
        secretReader,
        oldPartialConfig,
        newFullConfig,
        spec);
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
      return new TextNode(getOrThrowSecretValue(secretPersistence, coordinate));
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
                                              final JsonNode spec) {
    return internalSplitAndUpdateConfig(uuidSupplier, workspaceId, (coordinate) -> Optional.empty(), Jsons.emptyObject(), fullConfig,
        spec);
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
                                                       final JsonNode spec,
                                                       final ReadOnlySecretPersistence secretReader) {
    return internalSplitAndUpdateConfig(uuidSupplier, workspaceId, secretReader, oldPartialConfig, newFullConfig, spec);
  }

  /**
   * This returns all the unique path to the airbyte secrets based on a schema spec. The path will be
   * return in an ascending alphabetical order.
   */
  public static List<String> getSortedSecretPaths(final JsonNode spec) {
    return JsonSchemas.collectPathsThatMeetCondition(
        spec,
        node -> MoreIterators.toList(node.fields())
            .stream()
            .anyMatch(field -> AirbyteSecretConstants.AIRBYTE_SECRET_FIELD.equals(field.getKey())))
        .stream()
        .map(JsonPaths::mapJsonSchemaPathToJsonPath)
        .distinct()
        .sorted()
        .toList();
  }

  private static Optional<String> getExistingCoordinateIfExists(final JsonNode json) {
    if (json != null && json.has(COORDINATE_FIELD)) {
      return Optional.ofNullable(json.get(COORDINATE_FIELD).asText());
    } else {
      return Optional.empty();
    }
  }

  private static SecretCoordinate getOrCreateCoordinate(final ReadOnlySecretPersistence secretReader,
                                                        final UUID workspaceId,
                                                        final Supplier<UUID> uuidSupplier,
                                                        final JsonNode newJson,
                                                        final JsonNode persistedJson) {

    final Optional<String> existingCoordinateOptional = getExistingCoordinateIfExists(persistedJson);
    return getCoordinate(newJson.asText(), secretReader, workspaceId, uuidSupplier, existingCoordinateOptional.orElse(null));
  }

  /**
   * Internal method used to support both "split config" and "split and update config" operations.
   *
   * For splits that don't have a prior partial config (such as when a connector is created for a
   * source or destination for the first time), the secret reader and old partial config can be set to
   * empty (see {@link SecretsHelpers#splitConfig(UUID, JsonNode, JsonNode)}).
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
   * @param persistedPartialConfig previous partial config for this specific configuration
   * @param newFullConfig new config containing secrets that will be used to update the partial config
   * @param spec config specification
   * @return a partial config + a map of coordinates to secret payloads
   */
  @VisibleForTesting
  static SplitSecretConfig internalSplitAndUpdateConfig(final Supplier<UUID> uuidSupplier,
                                                        final UUID workspaceId,
                                                        final ReadOnlySecretPersistence secretReader,
                                                        final JsonNode persistedPartialConfig,
                                                        final JsonNode newFullConfig,
                                                        final JsonNode spec) {
    var fullConfigCopy = newFullConfig.deepCopy();
    final var secretMap = new HashMap<SecretCoordinate, String>();

    final List<String> paths = getSortedSecretPaths(spec);

    for (final String path : paths) {
      fullConfigCopy = JsonPaths.replaceAt(fullConfigCopy, path, (json, pathOfNode) -> {
        final Optional<JsonNode> persistedNode = JsonPaths.getSingleValue(persistedPartialConfig, pathOfNode);
        final SecretCoordinate coordinate = getOrCreateCoordinate(
            secretReader,
            workspaceId,
            uuidSupplier,
            json,
            persistedNode.orElse(null));

        secretMap.put(coordinate, json.asText());

        return Jsons.jsonNode(Map.of(COORDINATE_FIELD, coordinate.getFullCoordinate()));
      });
    }

    return new SplitSecretConfig(fullConfigCopy, secretMap);
  }

  /**
   * Extracts a secret value from the persistence and throws an exception if the secret is not
   * available.
   *
   * @param secretPersistence storage layer for secrets
   * @param coordinate reference to a secret in the persistence
   * @throws RuntimeException when a secret at that coordinate is not available in the persistence
   * @return a json string containing the secret value or a JSON
   */
  private static String getOrThrowSecretValue(final ReadOnlySecretPersistence secretPersistence,
                                              final SecretCoordinate coordinate) {
    final var secretValue = secretPersistence.read(coordinate);

    if (secretValue.isEmpty()) {
      throw new RuntimeException(String.format("That secret was not found in the store! Coordinate: %s", coordinate.getFullCoordinate()));
    }
    return secretValue.get();
  }

  private static SecretCoordinate getCoordinateFromTextNode(final JsonNode node) {
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
   * @param workspaceId workspace used for this config
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
    return getSecretCoordinate("airbyte_workspace_", newSecret, secretReader, workspaceId, uuidSupplier, oldSecretFullCoordinate);
  }

  public static String getCoordinatorBase(final String secretBasePrefix, final UUID secretBaseId, final Supplier<UUID> uuidSupplier) {
    return secretBasePrefix + secretBaseId + "_secret_" + uuidSupplier.get();
  }

  private static SecretCoordinate getSecretCoordinate(final String secretBasePrefix,
                                                      final String newSecret,
                                                      final ReadOnlySecretPersistence secretReader,
                                                      final UUID secretBaseId,
                                                      final Supplier<UUID> uuidSupplier,
                                                      final @Nullable String oldSecretFullCoordinate) {
    String coordinateBase = null;
    Long version = null;

    if (oldSecretFullCoordinate != null) {
      final var oldCoordinate = SecretCoordinate.fromFullCoordinate(oldSecretFullCoordinate);
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
      coordinateBase = getCoordinatorBase(secretBasePrefix, secretBaseId, uuidSupplier);
    }

    if (version == null) {
      version = 1L;
    }

    return new SecretCoordinate(coordinateBase, version);
  }

  /**
   * This method takes in the key (JSON key or HMAC key) of a workspace service account as a secret
   * and generates a co-ordinate for the secret so that the secret can be written in secret
   * persistence at the generated co-ordinate
   *
   * @param newSecret The JSON key or HMAC key value
   * @param secretReader To read the value from secret persistence for comparison with the new value
   * @param workspaceId of the service account
   * @param uuidSupplier provided to allow a test case to produce known UUIDs in order for easy *
   *        fixture creation.
   * @param oldSecretCoordinate a nullable full coordinate (base+version) retrieved from the *
   *        previous config
   * @param keyType HMAC ot JSON key
   * @return a coordinate (versioned reference to where the secret is stored in the persistence)
   */
  public static SecretCoordinateToPayload convertServiceAccountCredsToSecret(final String newSecret,
                                                                             final ReadOnlySecretPersistence secretReader,
                                                                             final UUID workspaceId,
                                                                             final Supplier<UUID> uuidSupplier,
                                                                             final @Nullable JsonNode oldSecretCoordinate,
                                                                             final String keyType) {
    final String oldSecretFullCoordinate =
        (oldSecretCoordinate != null && oldSecretCoordinate.has(COORDINATE_FIELD)) ? oldSecretCoordinate.get(COORDINATE_FIELD).asText()
            : null;
    final SecretCoordinate coordinateForStagingConfig = getSecretCoordinate("service_account_" + keyType + "_",
        newSecret,
        secretReader,
        workspaceId,
        uuidSupplier,
        oldSecretFullCoordinate);
    return new SecretCoordinateToPayload(coordinateForStagingConfig,
        newSecret,
        Jsons.jsonNode(Map.of(COORDINATE_FIELD,
            coordinateForStagingConfig.getFullCoordinate())));
  }

  /**
   * Takes in the secret coordinate in form of a JSON and fetches the secret from the store
   *
   * @param secretCoordinateAsJson The co-ordinate at which we expect the secret value to be present
   *        in the secret persistence
   * @param readOnlySecretPersistence The secret persistence
   * @return Original secret value as JsonNode
   */
  public static JsonNode hydrateSecretCoordinate(final JsonNode secretCoordinateAsJson,
                                                 final ReadOnlySecretPersistence readOnlySecretPersistence) {
    final var secretCoordinate = getCoordinateFromTextNode(secretCoordinateAsJson.get(COORDINATE_FIELD));
    return Jsons.deserialize(getOrThrowSecretValue(readOnlySecretPersistence, secretCoordinate));
  }

}

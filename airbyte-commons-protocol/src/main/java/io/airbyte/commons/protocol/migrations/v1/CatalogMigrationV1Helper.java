/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations.v1;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.protocol.migrations.util.SchemaMigrations;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;

/**
 * For the v0 to v1 migration, it appears that we are persisting some protocol objects without
 * version. Until this gets addressed more properly, this class contains the helper functions used
 * to handle this on the fly migration.
 *
 * Once persisted objects are versioned, this code should be deleted.
 */
public class CatalogMigrationV1Helper {

  /**
   * Performs an in-place migration of the schema from v0 to v1 if v0 data types are detected
   *
   * @param configuredAirbyteCatalog to migrate
   */
  public static void upgradeSchemaIfNeeded(final ConfiguredAirbyteCatalog configuredAirbyteCatalog) {
    if (containsV0DataTypes(configuredAirbyteCatalog)) {
      upgradeSchema(configuredAirbyteCatalog);
    }
  }

  /**
   * Performs an in-place migration of the schema from v0 to v1 if v0 data types are detected
   *
   * @param airbyteCatalog to migrate
   */
  public static void upgradeSchemaIfNeeded(final AirbyteCatalog airbyteCatalog) {
    if (containsV0DataTypes(airbyteCatalog)) {
      upgradeSchema(airbyteCatalog);
    }
  }

  /**
   * Performs an in-place migration of the schema from v0 to v1
   *
   * @param configuredAirbyteCatalog to migrate
   */
  private static void upgradeSchema(final ConfiguredAirbyteCatalog configuredAirbyteCatalog) {
    for (final var stream : configuredAirbyteCatalog.getStreams()) {
      SchemaMigrationV1.upgradeSchema(stream.getStream().getJsonSchema());
    }
  }

  /**
   * Performs an in-place migration of the schema from v0 to v1
   *
   * @param airbyteCatalog to migrate
   */
  private static void upgradeSchema(final AirbyteCatalog airbyteCatalog) {
    for (final var stream : airbyteCatalog.getStreams()) {
      SchemaMigrationV1.upgradeSchema(stream.getJsonSchema());
    }
  }

  /**
   * Returns true if catalog contains v0 data types
   */
  private static boolean containsV0DataTypes(final ConfiguredAirbyteCatalog configuredAirbyteCatalog) {
    if (configuredAirbyteCatalog == null) {
      return false;
    }

    return configuredAirbyteCatalog
        .getStreams()
        .stream().findFirst()
        .map(ConfiguredAirbyteStream::getStream)
        .map(CatalogMigrationV1Helper::streamContainsV0DataTypes)
        .orElse(false);
  }

  /**
   * Returns true if catalog contains v0 data types
   */
  private static boolean containsV0DataTypes(final AirbyteCatalog airbyteCatalog) {
    if (airbyteCatalog == null) {
      return false;
    }

    return airbyteCatalog
        .getStreams()
        .stream().findFirst()
        .map(CatalogMigrationV1Helper::streamContainsV0DataTypes)
        .orElse(false);
  }

  private static boolean streamContainsV0DataTypes(final AirbyteStream airbyteStream) {
    if (airbyteStream == null || airbyteStream.getJsonSchema() == null) {
      return false;
    }
    return hasV0DataType(airbyteStream.getJsonSchema());
  }

  /**
   * Performs of search of a v0 data type node, returns true at the first node found.
   */
  private static boolean hasV0DataType(final JsonNode schema) {
    if (SchemaMigrationV1.isPrimitiveTypeDeclaration(schema)) {
      return true;
    }

    for (final JsonNode subSchema : SchemaMigrations.findSubschemas(schema)) {
      if (hasV0DataType(subSchema)) {
        return true;
      }
    }
    return false;
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations.v1;

import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

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
   * @param configuredAirbyteCatalog to migrate
   */
  public static void upgradeSchemaIfNeeded(final ConfiguredAirbyteCatalog configuredAirbyteCatalog) {
    if (containsV0DataTypes(configuredAirbyteCatalog)) {
      upgradeSchema(configuredAirbyteCatalog);
    }
  }

  /**
   * Performs an in-place migration of the schema from v0 to v1
   *
   * @param configuredAirbyteCatalog to migrate
   */
  static void upgradeSchema(final ConfiguredAirbyteCatalog configuredAirbyteCatalog) {
    for (final var stream : configuredAirbyteCatalog.getStreams()) {
      SchemaMigrationV1.upgradeSchema(stream.getStream().getJsonSchema());
    }
  }

  /**
   * Returns true if catalog contains v0 data types
   */
  static boolean containsV0DataTypes(final ConfiguredAirbyteCatalog configuredAirbyteCatalog) {
    // TODO VERSIONING implement
    return false;
  }

}

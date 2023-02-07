/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

public interface ConfiguredAirbyteCatalogMigration<PreviousVersion, CurrentVersion> extends Migration {

  /**
   * Downgrades a ConfiguredAirbyteCatalog from the new version to the old version
   *
   * @param message: the ConfiguredAirbyteCatalog to downgrade
   * @return the downgraded ConfiguredAirbyteCatalog
   */
  PreviousVersion downgrade(final CurrentVersion message);

  /**
   * Upgrades a ConfiguredAirbyteCatalog from the old version to the new version
   *
   * @param message: the ConfiguredAirbyteCatalog to upgrade
   * @return the upgraded ConfiguredAirbyteCatalog
   */
  CurrentVersion upgrade(final PreviousVersion message);

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.protocol.migrations.ConfiguredAirbyteCatalogMigration;
import io.airbyte.commons.protocol.migrations.MigrationContainer;
import io.airbyte.commons.version.Version;
import jakarta.annotation.PostConstruct;
import jakarta.inject.Singleton;
import java.util.List;
import java.util.Set;

@Singleton
public class ConfiguredAirbyteCatalogMigrator {

  private final MigrationContainer<ConfiguredAirbyteCatalogMigration<?, ?>> migrationContainer;

  public ConfiguredAirbyteCatalogMigrator(final List<ConfiguredAirbyteCatalogMigration<?, ?>> migrations) {
    migrationContainer = new MigrationContainer<>(migrations);
  }

  @PostConstruct
  public void initialize() {
    migrationContainer.initialize();
  }

  /**
   * Downgrade a message from the most recent version to the target version by chaining all the
   * required migrations
   */
  public <PreviousVersion, CurrentVersion> PreviousVersion downgrade(final CurrentVersion message, final Version target) {
    return migrationContainer.downgrade(message, target, ConfiguredAirbyteCatalogMigrator::applyDowngrade);
  }

  /**
   * Upgrade a message from the source version to the most recent version by chaining all the required
   * migrations
   */
  public <PreviousVersion, CurrentVersion> CurrentVersion upgrade(final PreviousVersion message, final Version source) {
    return migrationContainer.upgrade(message, source, ConfiguredAirbyteCatalogMigrator::applyUpgrade);
  }

  public Version getMostRecentVersion() {
    return migrationContainer.getMostRecentVersion();
  }

  // Helper function to work around type casting
  private static <PreviousVersion, CurrentVersion> PreviousVersion applyDowngrade(final ConfiguredAirbyteCatalogMigration<PreviousVersion, CurrentVersion> migration,
                                                                                  final Object message) {
    return migration.downgrade((CurrentVersion) message);
  }

  // Helper function to work around type casting
  private static <PreviousVersion, CurrentVersion> CurrentVersion applyUpgrade(final ConfiguredAirbyteCatalogMigration<PreviousVersion, CurrentVersion> migration,
                                                                               final Object message) {
    return migration.upgrade((PreviousVersion) message);
  }

  // Used for inspection of the injection
  @VisibleForTesting
  Set<String> getMigrationKeys() {
    return migrationContainer.getMigrationKeys();
  }

}

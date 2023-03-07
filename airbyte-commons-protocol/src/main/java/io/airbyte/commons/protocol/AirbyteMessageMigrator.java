/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.protocol.migrations.AirbyteMessageMigration;
import io.airbyte.commons.version.Version;
import jakarta.annotation.PostConstruct;
import jakarta.inject.Singleton;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.SortedMap;
import java.util.TreeMap;

/**
 * AirbyteProtocol Message Migrator
 *
 * This class is intended to apply the transformations required to go from one version of the
 * AirbyteProtocol to another.
 */
@Singleton
public class AirbyteMessageMigrator {

  private final List<AirbyteMessageMigration<?, ?>> migrationsToRegister;
  private final SortedMap<String, AirbyteMessageMigration<?, ?>> migrations = new TreeMap<>();
  private String mostRecentMajorVersion = "";

  public AirbyteMessageMigrator(List<AirbyteMessageMigration<?, ?>> migrations) {
    migrationsToRegister = migrations;
  }

  public AirbyteMessageMigrator() {
    this(Collections.emptyList());
  }

  @PostConstruct
  public void initialize() {
    migrationsToRegister.forEach(this::registerMigration);
  }

  /**
   * Downgrade a message from the most recent version to the target version by chaining all the
   * required migrations
   */
  public <PreviousVersion, CurrentVersion> PreviousVersion downgrade(final CurrentVersion message, final Version target) {
    if (target.getMajorVersion().equals(mostRecentMajorVersion)) {
      return (PreviousVersion) message;
    }

    Object result = message;
    Object[] selectedMigrations = selectMigrations(target).toArray();
    for (int i = selectedMigrations.length; i > 0; --i) {
      result = applyDowngrade((AirbyteMessageMigration<?, ?>) selectedMigrations[i - 1], result);
    }
    return (PreviousVersion) result;
  }

  /**
   * Upgrade a message from the source version to the most recent version by chaining all the required
   * migrations
   */
  public <PreviousVersion, CurrentVersion> CurrentVersion upgrade(final PreviousVersion message, final Version source) {
    if (source.getMajorVersion().equals(mostRecentMajorVersion)) {
      return (CurrentVersion) message;
    }

    Object result = message;
    for (var migration : selectMigrations(source)) {
      result = applyUpgrade(migration, result);
    }
    return (CurrentVersion) result;
  }

  public Version getMostRecentVersion() {
    return new Version(mostRecentMajorVersion, "0", "0");
  }

  private Collection<AirbyteMessageMigration<?, ?>> selectMigrations(final Version version) {
    final Collection<AirbyteMessageMigration<?, ?>> results = migrations.tailMap(version.getMajorVersion()).values();
    if (results.isEmpty()) {
      throw new RuntimeException("Unsupported migration version " + version.serialize());
    }
    return results;
  }

  // Helper function to work around type casting
  private <PreviousVersion, CurrentVersion> PreviousVersion applyDowngrade(final AirbyteMessageMigration<PreviousVersion, CurrentVersion> migration,
                                                                           final Object message) {
    return migration.downgrade((CurrentVersion) message);
  }

  // Helper function to work around type casting
  private <PreviousVersion, CurrentVersion> CurrentVersion applyUpgrade(final AirbyteMessageMigration<PreviousVersion, CurrentVersion> migration,
                                                                        final Object message) {
    return migration.upgrade((PreviousVersion) message);
  }

  /**
   * Store migration in a sorted map key by the major of the lower version of the migration.
   *
   * The goal is to be able to retrieve the list of migrations to apply to get to/from a given
   * version. We are only keying on the lower version because the right side (most recent version of
   * the migration range) is always current version.
   */
  @VisibleForTesting
  void registerMigration(final AirbyteMessageMigration<?, ?> migration) {
    final String key = migration.getPreviousVersion().getMajorVersion();
    if (!migrations.containsKey(key)) {
      migrations.put(key, migration);
      if (migration.getCurrentVersion().getMajorVersion().compareTo(mostRecentMajorVersion) > 0) {
        mostRecentMajorVersion = migration.getCurrentVersion().getMajorVersion();
      }
    } else {
      throw new RuntimeException("Trying to register a duplicated migration " + migration.getClass().getName());
    }
  }

  // Used for inspection of the injection
  @VisibleForTesting
  Set<String> getMigrationKeys() {
    return migrations.keySet();
  }

}

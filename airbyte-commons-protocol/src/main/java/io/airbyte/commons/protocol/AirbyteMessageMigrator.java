/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.protocol.migrations.AirbyteMessageMigration;
import io.airbyte.commons.version.AirbyteVersion;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.SortedMap;
import java.util.TreeMap;
import jakarta.annotation.PostConstruct;
import jakarta.inject.Singleton;

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
  private String mostRecentVersion = "";

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
  public <Old, New> Old downgrade(final New message, final AirbyteVersion target) {
    if (target.getMajorVersion().equals(mostRecentVersion)) {
      return (Old) message;
    }

    Object result = message;
    Object[] selectedMigrations = selectMigrations(target).toArray();
    for (int i = selectedMigrations.length; i > 0; --i) {
      result = applyDowngrade((AirbyteMessageMigration<?, ?>) selectedMigrations[i - 1], result);
    }
    return (Old) result;
  }

  /**
   * Upgrade a message from the source version to the most recent version by chaining all the required
   * migrations
   */
  public <Old, New> New upgrade(final Old message, final AirbyteVersion source) {
    if (source.getMajorVersion().equals(mostRecentVersion)) {
      return (New) message;
    }

    Object result = message;
    for (var migration : selectMigrations(source)) {
      result = applyUpgrade(migration, result);
    }
    return (New) result;
  }

  private Collection<AirbyteMessageMigration<?, ?>> selectMigrations(final AirbyteVersion version) {
    final Collection<AirbyteMessageMigration<?, ?>> results = migrations.tailMap(version.getMajorVersion()).values();
    if (results.isEmpty()) {
      throw new RuntimeException("Unsupported migration version " + version.serialize());
    }
    return results;
  }

  // Helper function to work around type casting
  private <Old, New> Old applyDowngrade(final AirbyteMessageMigration<Old, New> migration, final Object message) {
    return migration.downgrade((New) message);
  }

  // Helper function to work around type casting
  private <Old, New> New applyUpgrade(final AirbyteMessageMigration<Old, New> migration, final Object message) {
    return migration.upgrade((Old) message);
  }

  @VisibleForTesting
  void registerMigration(final AirbyteMessageMigration<?, ?> migration) {
    final String key = migration.getOldVersion().getMajorVersion();
    if (!migrations.containsKey(key)) {
      migrations.put(key, migration);
      if (migration.getNewVersion().getMajorVersion().compareTo(mostRecentVersion) > 0) {
        mostRecentVersion = migration.getNewVersion().getMajorVersion();
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

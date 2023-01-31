/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import io.airbyte.commons.version.Version;
import java.util.Collection;
import java.util.List;
import java.util.Set;
import java.util.SortedMap;
import java.util.TreeMap;
import java.util.function.BiFunction;

public class MigrationContainer<T extends Migration> {

  private final List<T> migrationsToRegister;
  private final SortedMap<String, T> migrations = new TreeMap<>();
  private String mostRecentMajorVersion = "";

  public MigrationContainer(final List<T> migrations) {
    this.migrationsToRegister = migrations;
  }

  public void initialize() {
    migrationsToRegister.forEach(this::registerMigration);
  }

  public Version getMostRecentVersion() {
    return new Version(mostRecentMajorVersion, "0", "0");
  }

  /**
   * Downgrade a message from the most recent version to the target version by chaining all the
   * required migrations
   */
  public <PreviousVersion, CurrentVersion> PreviousVersion downgrade(final CurrentVersion message,
                                                                     final Version target,
                                                                     final BiFunction<T, Object, Object> applyDowngrade) {
    if (target.getMajorVersion().equals(mostRecentMajorVersion)) {
      return (PreviousVersion) message;
    }

    Object result = message;
    Object[] selectedMigrations = selectMigrations(target).toArray();
    for (int i = selectedMigrations.length; i > 0; --i) {
      result = applyDowngrade.apply((T) selectedMigrations[i - 1], result);
    }
    return (PreviousVersion) result;
  }

  /**
   * Upgrade a message from the source version to the most recent version by chaining all the required
   * migrations
   */
  public <PreviousVersion, CurrentVersion> CurrentVersion upgrade(final PreviousVersion message,
                                                                  final Version source,
                                                                  final BiFunction<T, Object, Object> applyUpgrade) {
    if (source.getMajorVersion().equals(mostRecentMajorVersion)) {
      return (CurrentVersion) message;
    }

    Object result = message;
    for (var migration : selectMigrations(source)) {
      result = applyUpgrade.apply(migration, result);
    }
    return (CurrentVersion) result;
  }

  public Collection<T> selectMigrations(final Version version) {
    final Collection<T> results = migrations.tailMap(version.getMajorVersion()).values();
    if (results.isEmpty()) {
      throw new RuntimeException("Unsupported migration version " + version.serialize());
    }
    return results;
  }

  /**
   * Store migration in a sorted map key by the major of the lower version of the migration.
   *
   * The goal is to be able to retrieve the list of migrations to apply to get to/from a given
   * version. We are only keying on the lower version because the right side (most recent version of
   * the migration range) is always current version.
   */
  private void registerMigration(final T migration) {
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

  public Set<String> getMigrationKeys() {
    return migrations.keySet();
  }

}

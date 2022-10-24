/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import io.airbyte.commons.version.Version;
import jakarta.inject.Singleton;

/**
 * Factory to build AirbyteMessageVersionedMigrator
 */
@Singleton
public class AirbyteMessageVersionedMigratorFactory {

  private final AirbyteMessageMigrator migrator;

  public AirbyteMessageVersionedMigratorFactory(final AirbyteMessageMigrator migrator) {
    this.migrator = migrator;
  }

  public <T> AirbyteMessageVersionedMigrator<T> getVersionedMigrator(final Version version) {
    return new AirbyteMessageVersionedMigrator<>(this.migrator, version);
  }

  public Version getMostRecentVersion() {
    return migrator.getMostRecentVersion();
  }

}

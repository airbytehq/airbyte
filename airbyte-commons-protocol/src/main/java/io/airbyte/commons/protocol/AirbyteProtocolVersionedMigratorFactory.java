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
public class AirbyteProtocolVersionedMigratorFactory {

  private final AirbyteMessageMigrator airbyteMessageMigrator;
  private final ConfiguredAirbyteCatalogMigrator configuredAirbyteCatalogMigrator;

  public AirbyteProtocolVersionedMigratorFactory(final AirbyteMessageMigrator airbyteMessageMigrator,
                                                 final ConfiguredAirbyteCatalogMigrator configuredAirbyteCatalogMigrator) {
    this.airbyteMessageMigrator = airbyteMessageMigrator;
    this.configuredAirbyteCatalogMigrator = configuredAirbyteCatalogMigrator;
  }

  public <T> AirbyteMessageVersionedMigrator<T> getAirbyteMessageMigrator(final Version version) {
    return new AirbyteMessageVersionedMigrator<>(airbyteMessageMigrator, version);
  }

  public final VersionedProtocolSerializer getProtocolSerializer(final Version version) {
    return new VersionedProtocolSerializer(configuredAirbyteCatalogMigrator, version);
  }

  public Version getMostRecentVersion() {
    return airbyteMessageMigrator.getMostRecentVersion();
  }

}

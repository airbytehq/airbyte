/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Optional;

/**
 * Wraps message migration from a fixed version to the most recent version
 */
public class AirbyteMessageVersionedMigrator<OriginalMessageType> {

  private final AirbyteMessageMigrator migrator;
  private final Version version;

  public AirbyteMessageVersionedMigrator(final AirbyteMessageMigrator migrator, final Version version) {
    this.migrator = migrator;
    this.version = version;
  }

  public OriginalMessageType downgrade(final AirbyteMessage message, final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
    return migrator.downgrade(message, version, configuredAirbyteCatalog);
  }

  public AirbyteMessage upgrade(final OriginalMessageType message, final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
    return migrator.upgrade(message, version, configuredAirbyteCatalog);
  }

  public Version getVersion() {
    return version;
  }

}

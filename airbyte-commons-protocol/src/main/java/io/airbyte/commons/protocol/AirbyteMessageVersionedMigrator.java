/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.v0.AirbyteMessage;

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

  public OriginalMessageType downgrade(final AirbyteMessage message) {
    return migrator.downgrade(message, version);
  }

  public AirbyteMessage upgrade(final OriginalMessageType message) {
    return migrator.upgrade(message, version);
  }

  public Version getVersion() {
    return version;
  }

}

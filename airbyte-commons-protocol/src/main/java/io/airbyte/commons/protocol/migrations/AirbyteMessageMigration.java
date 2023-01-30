/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Optional;

/**
 * AirbyteProtocol message migration interface
 *
 * @param <PreviousVersion> The Old AirbyteMessage type
 * @param <CurrentVersion> The New AirbyteMessage type
 */
public interface AirbyteMessageMigration<PreviousVersion, CurrentVersion> extends Migration {

  /**
   * Downgrades a message to from the new version to the old version
   *
   * @param message: the message to downgrade
   * @param configuredAirbyteCatalog: the ConfiguredAirbyteCatalog of the connection when applicable
   * @return the downgraded message
   */
  PreviousVersion downgrade(final CurrentVersion message, final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog);

  /**
   * Upgrades a message from the old version to the new version
   *
   * @param message: the message to upgrade
   * @param configuredAirbyteCatalog: the ConfiguredAirbyteCatalog of the connection when applicable
   * @return the upgrade message
   */
  CurrentVersion upgrade(final PreviousVersion message, final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog);

}

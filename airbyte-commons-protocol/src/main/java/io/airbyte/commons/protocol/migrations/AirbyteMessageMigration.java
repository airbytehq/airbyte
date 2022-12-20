/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

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
   * @return the downgraded message
   */
  PreviousVersion downgrade(final CurrentVersion message);

  /**
   * Upgrades a message from the old version to the new version
   *
   * @param message: the message to upgrade
   * @return the upgrade message
   */
  CurrentVersion upgrade(final PreviousVersion message);

}

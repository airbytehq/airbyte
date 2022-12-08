/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import io.airbyte.commons.version.Version;

/**
 * AirbyteProtocol message migration interface
 *
 * @param <PreviousVersion> The Old AirbyteMessage type
 * @param <CurrentVersion> The New AirbyteMessage type
 */
public interface AirbyteMessageMigration<PreviousVersion, CurrentVersion> {

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

  /**
   * The Old version, note that due to semver, the important piece of information is the Major.
   */
  Version getPreviousVersion();

  /**
   * The New version, note that due to semver, the important piece of information is the Major.
   */
  Version getCurrentVersion();

}

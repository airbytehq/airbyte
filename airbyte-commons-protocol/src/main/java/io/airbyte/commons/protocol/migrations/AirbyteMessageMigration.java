/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import io.airbyte.commons.version.AirbyteVersion;

/**
 * AirbyteProtocol message migration interface
 *
 * @param <Old> The Old AirbyteMessage type
 * @param <New> The New AirbyteMessage type
 */
public interface AirbyteMessageMigration<Old, New> {

  /**
   * Downgrades a message to from the new version to the old version
   *
   * @param message: the message to downgrade
   * @return the downgraded message
   */
  Old downgrade(final New message);

  /**
   * Upgrades a message from the old version to the new version
   *
   * @param message: the message to upgrade
   * @return the upgrade message
   */
  New upgrade(final Old message);

  /**
   * The Old version, note that due to semver, the important piece of information is the Major.
   */
  AirbyteVersion getOldVersion();

  /**
   * The New version, note that due to semver, the important piece of information is the Major.
   */
  AirbyteVersion getNewVersion();

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import io.airbyte.commons.version.AirbyteVersion;

public interface AirbyteMessageMigration<Old, New> {

  Old downgrade(final New message);

  New upgrade(final Old message);

  AirbyteVersion getOldVersion();

  AirbyteVersion getNewVersion();

}

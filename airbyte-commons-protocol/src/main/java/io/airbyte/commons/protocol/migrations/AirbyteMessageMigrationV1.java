/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import jakarta.inject.Singleton;

/**
 * Placeholder AirbyteMessage Migration from v0 to v1
 */
@Singleton
public class AirbyteMessageMigrationV1 implements AirbyteMessageMigration<AirbyteMessage, io.airbyte.protocol.models.AirbyteMessage> {

  @Override
  public AirbyteMessage downgrade(io.airbyte.protocol.models.AirbyteMessage message) {
    return Jsons.object(Jsons.jsonNode(message), AirbyteMessage.class);
  }

  @Override
  public io.airbyte.protocol.models.AirbyteMessage upgrade(AirbyteMessage message) {
    return Jsons.object(Jsons.jsonNode(message), io.airbyte.protocol.models.AirbyteMessage.class);
  }

  @Override
  public Version getPreviousVersion() {
    return new Version("0.0.0");
  }

  @Override
  public Version getCurrentVersion() {
    return new Version("1.0.0");
  }

}

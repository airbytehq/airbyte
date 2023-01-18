/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.AirbyteMessage;
import jakarta.inject.Singleton;

/**
 * Demo migration to illustrate the template. This should be deleted once we added the v0 to v1
 * migration.
 */
@Singleton
public class AirbyteMessageMigrationV0
    implements AirbyteMessageMigration<AirbyteMessage, io.airbyte.protocol.models.v0.AirbyteMessage> {

  @Override
  public io.airbyte.protocol.models.v0.AirbyteMessage upgrade(final io.airbyte.protocol.models.AirbyteMessage oldMessage) {
    final io.airbyte.protocol.models.v0.AirbyteMessage newMessage =
        Jsons.object(Jsons.jsonNode(oldMessage), io.airbyte.protocol.models.v0.AirbyteMessage.class);
    return newMessage;
  }

  @Override
  public io.airbyte.protocol.models.AirbyteMessage downgrade(final io.airbyte.protocol.models.v0.AirbyteMessage newMessage) {
    final io.airbyte.protocol.models.AirbyteMessage oldMessage =
        Jsons.object(Jsons.jsonNode(newMessage), io.airbyte.protocol.models.AirbyteMessage.class);
    return oldMessage;
  }

  @Override
  public Version getPreviousVersion() {
    return new Version("0.2.0");
  }

  @Override
  public Version getCurrentVersion() {
    return new Version("0.2.0");
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.protocol.models.AirbyteMessage;

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
  public AirbyteVersion getOldVersion() {
    return new AirbyteVersion("default");
  }

  @Override
  public AirbyteVersion getNewVersion() {
    return new AirbyteVersion("0.2.0");
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import jakarta.inject.Singleton;

@Singleton
public class AirbyteMessageMigrationV1
    implements AirbyteMessageMigration<io.airbyte.protocol.models.v0.AirbyteMessage, io.airbyte.protocol.models.v1.AirbyteMessage> {

  @Override
  public AirbyteMessage downgrade(io.airbyte.protocol.models.v1.AirbyteMessage message) {
    return Jsons.object(Jsons.jsonNode(message), io.airbyte.protocol.models.v0.AirbyteMessage.class);
  }

  @Override
  public io.airbyte.protocol.models.v1.AirbyteMessage upgrade(AirbyteMessage message) {
    return Jsons.object(Jsons.jsonNode(message), io.airbyte.protocol.models.v1.AirbyteMessage.class);
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

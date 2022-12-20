/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import jakarta.inject.Singleton;
import java.util.Optional;

/**
 * Placeholder AirbyteMessage Migration from v0 to v1
 */
@Singleton
public class AirbyteMessageMigrationV1 implements AirbyteMessageMigration<AirbyteMessage, io.airbyte.protocol.models.AirbyteMessage> {

  @Override
  public AirbyteMessage downgrade(final io.airbyte.protocol.models.AirbyteMessage message,
                                  final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
    return Jsons.object(Jsons.jsonNode(message), AirbyteMessage.class);
  }

  @Override
  public io.airbyte.protocol.models.AirbyteMessage upgrade(final AirbyteMessage message,
                                                           final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
    return Jsons.object(Jsons.jsonNode(message), io.airbyte.protocol.models.AirbyteMessage.class);
  }

  @Override
  public Version getPreviousVersion() {
    return AirbyteProtocolVersion.V0;
  }

  @Override
  public Version getCurrentVersion() {
    return AirbyteProtocolVersion.V1;
  }

}

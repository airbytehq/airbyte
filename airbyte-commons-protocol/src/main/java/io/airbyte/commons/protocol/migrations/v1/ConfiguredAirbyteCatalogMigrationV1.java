/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations.v1;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.protocol.migrations.ConfiguredAirbyteCatalogMigration;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import jakarta.inject.Singleton;

@Singleton
public class ConfiguredAirbyteCatalogMigrationV1
    implements ConfiguredAirbyteCatalogMigration<io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog, ConfiguredAirbyteCatalog> {

  @Override
  public io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog downgrade(final ConfiguredAirbyteCatalog oldMessage) {
    final io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog newMessage = Jsons.object(
        Jsons.jsonNode(oldMessage),
        io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog.class);
    for (final io.airbyte.protocol.models.v0.ConfiguredAirbyteStream stream : newMessage.getStreams()) {
      final JsonNode schema = stream.getStream().getJsonSchema();
      SchemaMigrationV1.downgradeSchema(schema);
    }
    return newMessage;
  }

  @Override
  public ConfiguredAirbyteCatalog upgrade(final io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog oldMessage) {
    final ConfiguredAirbyteCatalog newMessage = Jsons.object(
        Jsons.jsonNode(oldMessage),
        ConfiguredAirbyteCatalog.class);
    for (final ConfiguredAirbyteStream stream : newMessage.getStreams()) {
      final JsonNode schema = stream.getStream().getJsonSchema();
      SchemaMigrationV1.upgradeSchema(schema);
    }
    return newMessage;
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

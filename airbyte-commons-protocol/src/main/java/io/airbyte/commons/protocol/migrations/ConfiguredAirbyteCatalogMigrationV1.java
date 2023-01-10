/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import jakarta.inject.Singleton;

@Singleton
public class ConfiguredAirbyteCatalogMigrationV1
    implements ConfiguredAirbyteCatalogMigration<ConfiguredAirbyteCatalog, io.airbyte.protocol.models.ConfiguredAirbyteCatalog> {

  @Override
  public ConfiguredAirbyteCatalog downgrade(io.airbyte.protocol.models.ConfiguredAirbyteCatalog message) {
    return Jsons.object(Jsons.jsonNode(message), ConfiguredAirbyteCatalog.class);
  }

  @Override
  public io.airbyte.protocol.models.ConfiguredAirbyteCatalog upgrade(ConfiguredAirbyteCatalog message) {
    return Jsons.object(Jsons.jsonNode(message), io.airbyte.protocol.models.ConfiguredAirbyteCatalog.class);
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

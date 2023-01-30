/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

/**
 * Serialize a ConfiguredAirbyteCatalog to the specified version
 * <p>
 * This Serializer expects a ConfiguredAirbyteCatalog from the Current version of the platform,
 * converts it to the target protocol version before serializing it.
 */
public class VersionedProtocolSerializer implements ProtocolSerializer {

  private final ConfiguredAirbyteCatalogMigrator configuredAirbyteCatalogMigrator;
  private final Version protocolVersion;

  public VersionedProtocolSerializer(final ConfiguredAirbyteCatalogMigrator configuredAirbyteCatalogMigrator, final Version protocolVersion) {
    this.configuredAirbyteCatalogMigrator = configuredAirbyteCatalogMigrator;
    this.protocolVersion = protocolVersion;
  }

  @Override
  public String serialize(final ConfiguredAirbyteCatalog configuredAirbyteCatalog) {
    return Jsons.serialize(configuredAirbyteCatalogMigrator.downgrade(configuredAirbyteCatalog, protocolVersion));
  }

}

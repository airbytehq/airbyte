/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.commons.protocol.AirbyteMessageSerDeProvider;
import io.airbyte.commons.protocol.AirbyteProtocolVersionedMigratorFactory;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.BufferedWriter;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class VersionedAirbyteMessageBufferedWriterFactory implements AirbyteMessageBufferedWriterFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(VersionedAirbyteMessageBufferedWriterFactory.class);

  private final AirbyteMessageSerDeProvider serDeProvider;
  private final AirbyteProtocolVersionedMigratorFactory migratorFactory;
  private final Version protocolVersion;
  private final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog;

  public VersionedAirbyteMessageBufferedWriterFactory(final AirbyteMessageSerDeProvider serDeProvider,
                                                      final AirbyteProtocolVersionedMigratorFactory migratorFactory,
                                                      final Version protocolVersion,
                                                      final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
    this.serDeProvider = serDeProvider;
    this.migratorFactory = migratorFactory;
    this.protocolVersion = protocolVersion;
    this.configuredAirbyteCatalog = configuredAirbyteCatalog;
  }

  @Override
  public AirbyteMessageBufferedWriter createWriter(BufferedWriter bufferedWriter) {
    final boolean needMigration = !protocolVersion.getMajorVersion().equals(migratorFactory.getMostRecentVersion().getMajorVersion());
    LOGGER.info(
        "Writing messages to protocol version {}{}",
        protocolVersion.serialize(),
        needMigration ? ", messages will be downgraded from protocol version " + migratorFactory.getMostRecentVersion().serialize() : "");
    return new VersionedAirbyteMessageBufferedWriter<>(
        bufferedWriter,
        serDeProvider.getSerializer(protocolVersion).orElseThrow(),
        migratorFactory.getAirbyteMessageMigrator(protocolVersion),
        configuredAirbyteCatalog);
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.commons.protocol.AirbyteMessageSerDeProvider;
import io.airbyte.commons.protocol.AirbyteMessageVersionedMigratorFactory;
import io.airbyte.commons.version.Version;
import java.io.BufferedWriter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class VersionedAirbyteMessageBufferedWriterFactory implements AirbyteMessageBufferedWriterFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(VersionedAirbyteMessageBufferedWriterFactory.class);

  private final AirbyteMessageSerDeProvider serDeProvider;
  private final AirbyteMessageVersionedMigratorFactory migratorFactory;
  private final Version protocolVersion;

  public VersionedAirbyteMessageBufferedWriterFactory(final AirbyteMessageSerDeProvider serDeProvider,
                                                      final AirbyteMessageVersionedMigratorFactory migratorFactory,
                                                      final Version protocolVersion) {
    this.serDeProvider = serDeProvider;
    this.migratorFactory = migratorFactory;
    this.protocolVersion = protocolVersion;
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
        migratorFactory.getVersionedMigrator(protocolVersion));
  }

}

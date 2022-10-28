/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.commons.protocol.AirbyteMessageSerDeProvider;
import io.airbyte.commons.protocol.AirbyteMessageVersionedMigratorFactory;
import io.airbyte.commons.version.Version;
import java.io.BufferedWriter;

public class VersionedAirbyteMessageBufferedWriterFactory implements AirbyteMessageBufferedWriterFactory {

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
    return new VersionedAirbyteMessageBufferedWriter<>(
        bufferedWriter,
        serDeProvider.getSerializer(protocolVersion).orElseThrow(),
        migratorFactory.getVersionedMigrator(protocolVersion));
  }

}

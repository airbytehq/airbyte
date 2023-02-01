/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.commons.protocol.AirbyteMessageVersionedMigrator;
import io.airbyte.commons.protocol.serde.AirbyteMessageSerializer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.BufferedWriter;
import java.io.IOException;
import java.util.Optional;

public class VersionedAirbyteMessageBufferedWriter<T> extends DefaultAirbyteMessageBufferedWriter {

  private final AirbyteMessageSerializer<T> serializer;
  private final AirbyteMessageVersionedMigrator<T> migrator;
  private final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog;

  public VersionedAirbyteMessageBufferedWriter(final BufferedWriter writer,
                                               final AirbyteMessageSerializer<T> serializer,
                                               final AirbyteMessageVersionedMigrator<T> migrator,
                                               final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
    super(writer);
    this.serializer = serializer;
    this.migrator = migrator;
    this.configuredAirbyteCatalog = configuredAirbyteCatalog;
  }

  @Override
  public void write(final AirbyteMessage message) throws IOException {
    final T downgradedMessage = migrator.downgrade(message, configuredAirbyteCatalog);
    writer.write(serializer.serialize(downgradedMessage));
    writer.newLine();
  }

}

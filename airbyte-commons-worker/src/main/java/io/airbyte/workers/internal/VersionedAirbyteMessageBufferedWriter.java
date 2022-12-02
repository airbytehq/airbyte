/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.commons.protocol.AirbyteMessageVersionedMigrator;
import io.airbyte.commons.protocol.serde.AirbyteMessageSerializer;
import io.airbyte.protocol.models.AirbyteMessage;
import java.io.BufferedWriter;
import java.io.IOException;

public class VersionedAirbyteMessageBufferedWriter<T> extends DefaultAirbyteMessageBufferedWriter {

  private final AirbyteMessageSerializer<T> serializer;
  private final AirbyteMessageVersionedMigrator<T> migrator;

  public VersionedAirbyteMessageBufferedWriter(final BufferedWriter writer,
                                               final AirbyteMessageSerializer<T> serializer,
                                               final AirbyteMessageVersionedMigrator<T> migrator) {
    super(writer);
    this.serializer = serializer;
    this.migrator = migrator;
  }

  @Override
  public void write(final AirbyteMessage message) throws IOException {
    final T downgradedMessage = migrator.downgrade(message);
    writer.write(serializer.serialize(downgradedMessage));
    writer.newLine();
  }

}

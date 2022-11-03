/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.commons.json.Jsons;
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
    final T downgradedMessage = migrator.downgrade(convert(message));
    writer.write(serializer.serialize(downgradedMessage));
    writer.newLine();
  }

  // TODO remove this conversion once we migrated default AirbyteMessage to be from a versioned
  // namespace
  private io.airbyte.protocol.models.v0.AirbyteMessage convert(final AirbyteMessage message) {
    return Jsons.object(Jsons.jsonNode(message), io.airbyte.protocol.models.v0.AirbyteMessage.class);
  }

}

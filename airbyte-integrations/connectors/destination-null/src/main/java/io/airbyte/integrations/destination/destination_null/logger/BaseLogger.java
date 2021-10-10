package io.airbyte.integrations.destination.destination_null.logger;

import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseLogger implements NullDestinationLogger {

  protected final AirbyteStreamNameNamespacePair streamNamePair;
  protected final int maxEntryCount;
  protected int loggedEntryCount = 0;

  public BaseLogger(AirbyteStreamNameNamespacePair streamNamePair, int maxEntryCount) {
    this.streamNamePair = streamNamePair;
    this.maxEntryCount = maxEntryCount;
  }

  protected String entryMessage(AirbyteRecordMessage recordMessage) {
    return String.format("[%s] %s #%04d: %s",
        emissionTimestamp(recordMessage.getEmittedAt()),
        streamName(streamNamePair),
        loggedEntryCount,
        recordMessage.getData());
  }

  protected static String streamName(AirbyteStreamNameNamespacePair pair) {
    if (pair.getNamespace() == null) {
      return pair.getName();
    } else {
      return String.format("%s.%s", pair.getNamespace(), pair.getName());
    }
  }

  protected static String emissionTimestamp(long emittedAt) {
    return OffsetDateTime
        .ofInstant(Instant.ofEpochMilli(emittedAt), ZoneId.systemDefault())
        .format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test.logging;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

public abstract class BaseLogger implements TestingLogger {

  protected final AirbyteStreamNameNamespacePair streamNamePair;
  protected final int maxEntryCount;
  protected int loggedEntryCount = 0;

  public BaseLogger(final AirbyteStreamNameNamespacePair streamNamePair, final int maxEntryCount) {
    this.streamNamePair = streamNamePair;
    this.maxEntryCount = maxEntryCount;
  }

  protected String entryMessage(final AirbyteRecordMessage recordMessage) {
    return String.format("[%s] %s #%04d: %s",
        emissionTimestamp(recordMessage.getEmittedAt()),
        streamName(streamNamePair),
        loggedEntryCount,
        recordMessage.getData());
  }

  protected static String streamName(final AirbyteStreamNameNamespacePair pair) {
    if (pair.getNamespace() == null) {
      return pair.getName();
    } else {
      return String.format("%s.%s", pair.getNamespace(), pair.getName());
    }
  }

  protected static String emissionTimestamp(final long emittedAt) {
    return OffsetDateTime
        .ofInstant(Instant.ofEpochMilli(emittedAt), ZoneId.systemDefault())
        .format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);
  }

}

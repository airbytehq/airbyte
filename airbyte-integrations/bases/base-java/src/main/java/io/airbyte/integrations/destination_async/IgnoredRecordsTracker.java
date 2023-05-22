/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashMap;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class IgnoredRecordsTracker {

  private static final Logger LOGGER = LoggerFactory.getLogger(IgnoredRecordsTracker.class);

  private final Map<StreamDescriptor, Long> streamToIgnoredRecordCount;

  public IgnoredRecordsTracker() {
    this(new HashMap<>());
  }

  @VisibleForTesting
  IgnoredRecordsTracker(final Map<StreamDescriptor, Long> streamToIgnoredRecordCount) {
    this.streamToIgnoredRecordCount = streamToIgnoredRecordCount;
  }

  public void addRecord(final StreamDescriptor streamDescriptor, final AirbyteMessage recordMessage) {
    streamToIgnoredRecordCount.put(streamDescriptor, streamToIgnoredRecordCount.getOrDefault(streamDescriptor, 0L) + 1L);
  }

  public void report() {
    streamToIgnoredRecordCount
        .forEach((pair, count) -> LOGGER.warn("A total of {} record(s) of data from stream {} were invalid and were ignored.", count, pair));
  }

}

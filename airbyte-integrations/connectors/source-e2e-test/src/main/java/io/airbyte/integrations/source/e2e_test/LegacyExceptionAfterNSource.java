/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.v0.*;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import java.time.Instant;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Throws an exception after it emits N record messages where N == throw_after_n_records. Ever 5th
 * message emitted is a state message. State messages do NOT count against N.
 */
public class LegacyExceptionAfterNSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(LegacyExceptionAfterNSource.class);

  static final AirbyteCatalog CATALOG = Jsons.clone(LegacyConstants.DEFAULT_CATALOG);
  static {
    CATALOG.getStreams().get(0).setSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    CATALOG.getStreams().get(0).setSourceDefinedCursor(true);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) {
    return Jsons.clone(CATALOG);
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final JsonNode state) {
    final long throwAfterNRecords = config.get("throw_after_n_records").asLong();

    final AtomicLong recordsEmitted = new AtomicLong();
    final AtomicLong recordValue;
    if (state != null && state.has(LegacyConstants.DEFAULT_COLUMN)) {
      LOGGER.info("Found state: {}", state);
      recordValue = new AtomicLong(state.get(LegacyConstants.DEFAULT_COLUMN).asLong());
    } else {
      LOGGER.info("No state found.");
      recordValue = new AtomicLong();
    }

    final AtomicBoolean hasEmittedStateAtCount = new AtomicBoolean();
    return AutoCloseableIterators.fromIterator(new AbstractIterator<>() {

      @Override
      protected AirbyteMessage computeNext() {
        if (recordsEmitted.get() % 5 == 0 && !hasEmittedStateAtCount.get()) {

          LOGGER.info("{}: emitting state record with value {}", LegacyExceptionAfterNSource.class, recordValue.get());

          hasEmittedStateAtCount.set(true);
          return new AirbyteMessage()
              .withType(Type.STATE)
              .withState(new AirbyteStateMessage()
                  .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                  .withStream(new AirbyteStreamState()
                      .withStreamDescriptor(new StreamDescriptor().withName(LegacyConstants.DEFAULT_STREAM))
                      .withStreamState(Jsons.jsonNode(ImmutableMap.of(LegacyConstants.DEFAULT_COLUMN, recordValue.get()))))
                  .withData(Jsons.jsonNode(ImmutableMap.of(LegacyConstants.DEFAULT_COLUMN, recordValue.get()))));
        } else if (throwAfterNRecords > recordsEmitted.get()) {
          recordsEmitted.incrementAndGet();
          recordValue.incrementAndGet();
          hasEmittedStateAtCount.set(false);

          LOGGER.info("{} ExceptionAfterNSource: emitting record with value {}. record {} in sync.",
              LegacyExceptionAfterNSource.class, recordValue.get(), recordsEmitted.get());

          return new AirbyteMessage()
              .withType(Type.RECORD)
              .withRecord(new AirbyteRecordMessage()
                  .withStream(LegacyConstants.DEFAULT_STREAM)
                  .withEmittedAt(Instant.now().toEpochMilli())
                  .withData(Jsons.jsonNode(ImmutableMap.of(LegacyConstants.DEFAULT_COLUMN, recordValue.get()))));
        } else {
          throw new IllegalStateException("Scheduled exceptional event.");
        }
      }

    });
  }

}

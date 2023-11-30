/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertAll;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import io.airbyte.workers.internal.AirbyteDestination;
import java.util.List;
import org.junit.jupiter.api.Test;

public class RedshiftStandardInsertsTypingDedupingTest extends AbstractRedshiftTypingDedupingTest {

  @Override
  protected String getConfigPath() {
    return "secrets/1s1t_config.json";
  }

  /**
   * This test is identical to the one in {@link io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest}, except that it only
   * emits just 1K messages instead of 100k. Redshift isn't optimized for standard inserts, so it takes painfully long time for the test to complete.
   * In manual test observation, it took 2 mins to insert 2K records and keeps increasing as the batch size grows.
   * @throws Exception
   */
  @Test
  @Override
  public void identicalNameSimultaneousSync() throws Exception {
    final String namespace1 = streamNamespace + "_1";
    final ConfiguredAirbyteCatalog catalog1 = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                            .withNamespace(namespace1)
                            .withName(streamName)
                            .withJsonSchema(SCHEMA))));

    final String namespace2 = streamNamespace + "_2";
    final ConfiguredAirbyteCatalog catalog2 = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                            .withNamespace(namespace2)
                            .withName(streamName)
                            .withJsonSchema(SCHEMA))));

    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl", namespace1, streamName);
    final List<AirbyteMessage> messages2 = readMessages("dat/sync1_messages2.jsonl", namespace2, streamName);

    // Start two concurrent syncs
    final AirbyteDestination sync1 = startSync(catalog1);
    final AirbyteDestination sync2 = startSync(catalog2);
    // Write some messages to both syncs. Write a lot of data to sync 2 to try and force a flush.
    pushMessages(messages1, sync1);
    for (int i = 0; i < 1_000; i++) {
      pushMessages(messages2, sync2);
    }
    // This will dump sync1's entire stdout to our stdout
    endSync(sync1);
    // Write some more messages to the second sync. It should not be affected by the first sync's
    // shutdown.
    for (int i = 0; i < 1_000; i++) {
      pushMessages(messages2, sync2);
    }
    // And this will dump sync2's entire stdout to our stdout
    endSync(sync2);

    // For simplicity, don't verify the raw table. Assume that if the final table is correct, then
    // the raw data is correct. This is generally a safe assumption.
    assertAll(
        () -> DIFFER.diffFinalTableRecords(
            readRecords("dat/sync1_expectedrecords_dedup_final.jsonl"),
            dumpFinalTableRecords(namespace1, streamName)),
        () -> DIFFER.diffFinalTableRecords(
            readRecords("dat/sync1_expectedrecords_dedup_final2.jsonl"),
            dumpFinalTableRecords(namespace2, streamName)));
  }

}

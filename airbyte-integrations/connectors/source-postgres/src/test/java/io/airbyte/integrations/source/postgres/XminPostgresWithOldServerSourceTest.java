/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.extractStateMessage;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.filterRecords;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.setEmittedAtToNull;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateStats;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

public class XminPostgresWithOldServerSourceTest extends XminPostgresSourceTest {

  @Override
  protected BaseImage getDatabaseImage() {
    return BaseImage.POSTGRES_9;
  }

  @Test
  @Override
  void testReadSuccess() throws Exception {
    // Perform an initial sync with the configured catalog, which is set up to use xmin_replication.
    // All of the records in the configured stream should be emitted.
    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_XMIN_CATALOG
            .withStreams(CONFIGURED_XMIN_CATALOG.getStreams().stream().filter(s -> s.getStream().getName().equals(STREAM_NAME)).collect(
                Collectors.toList()));
    final List<AirbyteMessage> recordsFromFirstSync =
        MoreIterators.toList(source().read(getXminConfig(), configuredCatalog, null));
    setEmittedAtToNull(recordsFromFirstSync);
    assertThat(filterRecords(recordsFromFirstSync)).containsExactlyElementsOf(INITIAL_RECORD_MESSAGES);

    // Extract the state message and assert that it exists. It contains the xmin value, so validating
    // the actual value isn't useful right now.
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessage(recordsFromFirstSync);
    assertEquals(1, stateAfterFirstBatch.size());

    final AirbyteStateMessage firstSyncStateMessage = stateAfterFirstBatch.get(0);
    final String stateTypeFromFirstStateMessage = firstSyncStateMessage.getStream().getStreamState().get("state_type").asText();

    // Since the flow reclassified the stream to do initial load using xmin
    // It should only contain a single final state of xmin type.
    assertEquals("xmin", stateTypeFromFirstStateMessage);
    assertFalse(firstSyncStateMessage.getStream().getStreamState().has("ctid"));
    assertFalse(firstSyncStateMessage.getStream().getStreamState().has("incremental_state"));

    // Assert that the last message in the sequence is a state message
    assertMessageSequence(recordsFromFirstSync);

    // Read with the final xmin state message should return no data
    final List<AirbyteMessage> syncWithXminStateType =
        MoreIterators.toList(source().read(getXminConfig(), configuredCatalog,
            Jsons.jsonNode(Collections.singletonList(firstSyncStateMessage))));
    setEmittedAtToNull(syncWithXminStateType);
    assertEquals(0, filterRecords(syncWithXminStateType).size());

    // Even though no records were emitted, a state message is still expected
    final List<AirbyteStateMessage> stateAfterXminSync = extractStateMessage(syncWithXminStateType);
    assertEquals(1, stateAfterXminSync.size());
    // Since no records were returned so the state should be the same as before; just without the
    // counts.
    firstSyncStateMessage.setSourceStats(new AirbyteStateStats().withRecordCount(0.0));
    assertEquals(firstSyncStateMessage, stateAfterXminSync.get(0));

    // We add some data and perform a third read. We should verify that (i) a delete is not captured and
    // (ii) the new record that is inserted into the
    // table is read.
    testdb.query(ctx -> {
      ctx.fetch("DELETE FROM id_and_name WHERE id = 'NaN';");
      ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (3, 'gohan', 222.1);");
      return null;
    });

    final List<AirbyteMessage> recordsAfterLastSync =
        MoreIterators.toList(source().read(getXminConfig(), configuredCatalog,
            Jsons.jsonNode(Collections.singletonList(stateAfterXminSync.get(0)))));
    setEmittedAtToNull(recordsAfterLastSync);
    assertThat(filterRecords(recordsAfterLastSync)).containsExactlyElementsOf(NEXT_RECORD_MESSAGES);
    assertMessageSequence(recordsAfterLastSync);
    final List<AirbyteStateMessage> stateAfterLastSync = extractStateMessage(recordsAfterLastSync);
    assertEquals(1, stateAfterLastSync.size());

    final AirbyteStateMessage finalStateMesssage = stateAfterLastSync.get(0);
    final String stateTypeFromFinalStateMessage = finalStateMesssage.getStream().getStreamState().get("state_type").asText();
    assertEquals("xmin", stateTypeFromFinalStateMessage);
    assertTrue(finalStateMesssage.getStream().getStreamState().get("xmin_xid_value").asLong() > firstSyncStateMessage.getStream().getStreamState()
        .get("xmin_xid_value").asLong());
    assertTrue(finalStateMesssage.getStream().getStreamState().get("xmin_raw_value").asLong() > firstSyncStateMessage.getStream().getStreamState()
        .get("xmin_raw_value").asLong());
  }

}

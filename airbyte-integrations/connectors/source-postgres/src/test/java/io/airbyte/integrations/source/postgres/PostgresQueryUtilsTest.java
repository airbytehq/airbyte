/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.integrations.source.postgres.internal.models.CursorBasedStatus;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for PostgresQueryUtils, specifically testing the handling of streams
 * without cursor fields (e.g., full_refresh streams with empty cursorField).
 */
public class PostgresQueryUtilsTest {

  private static final String QUOTE_STRING = "\"";

  /**
   * Test that getCursorBasedSyncStatusForStreams handles streams with null cursor field
   * gracefully without generating invalid SQL queries.
   *
   * This test addresses GitHub issue #70356 where resumable full refresh generates
   * invalid SQL with null cursor field: "ERROR: column "null" does not exist"
   */
  @Test
  public void testGetCursorBasedSyncStatusForStreamsWithNullCursorField() throws Exception {
    // Create a mock database - we don't need it to return anything since
    // streams with null cursor should skip the query
    final JdbcDatabase mockDatabase = mock(JdbcDatabase.class);

    // Create a full refresh stream with no cursor field
    final ConfiguredAirbyteStream fullRefreshStream = CatalogHelpers.toDefaultConfiguredStream(
        CatalogHelpers.createAirbyteStream(
            "test_stream",
            "test_schema",
            Field.of("id", JsonSchemaType.INTEGER),
            Field.of("name", JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withCursorField(Collections.emptyList()); // Empty cursor field

    // Create a mock state manager that returns CursorInfo with null cursor field
    final StateManager mockStateManager = mock(StateManager.class);
    final CursorInfo cursorInfoWithNullField = new CursorInfo(null, null, null, null);
    when(mockStateManager.getCursorInfo(any(io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair.class)))
        .thenReturn(Optional.of(cursorInfoWithNullField));

    // Call the method under test
    final Map<AirbyteStreamNameNamespacePair, CursorBasedStatus> result =
        PostgresQueryUtils.getCursorBasedSyncStatusForStreams(
            mockDatabase,
            List.of(fullRefreshStream),
            mockStateManager,
            QUOTE_STRING);

    // Verify that the stream is in the result map with a valid status
    assertEquals(1, result.size());

    final AirbyteStreamNameNamespacePair streamPair =
        new AirbyteStreamNameNamespacePair("test_stream", "test_schema");
    final CursorBasedStatus status = result.get(streamPair);

    assertNotNull(status, "Status should not be null for stream with null cursor field");
    assertEquals("test_stream", status.getStreamName());
    assertEquals("test_schema", status.getStreamNamespace());
    assertEquals(StateType.CURSOR_BASED, status.getStateType());
    assertEquals(2L, status.getVersion());
    assertTrue(status.getCursorField().isEmpty(), "Cursor field should be empty list");
  }

  /**
   * Test that getCursorBasedSyncStatusForStreams handles streams with empty string cursor field
   * gracefully without generating invalid SQL queries.
   */
  @Test
  public void testGetCursorBasedSyncStatusForStreamsWithEmptyCursorField() throws Exception {
    // Create a mock database
    final JdbcDatabase mockDatabase = mock(JdbcDatabase.class);

    // Create a stream
    final ConfiguredAirbyteStream stream = CatalogHelpers.toDefaultConfiguredStream(
        CatalogHelpers.createAirbyteStream(
            "test_stream",
            "test_schema",
            Field.of("id", JsonSchemaType.INTEGER),
            Field.of("name", JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withCursorField(Collections.emptyList());

    // Create a mock state manager that returns CursorInfo with empty string cursor field
    final StateManager mockStateManager = mock(StateManager.class);
    final CursorInfo cursorInfoWithEmptyField = new CursorInfo(null, null, "", null);
    when(mockStateManager.getCursorInfo(any(io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair.class)))
        .thenReturn(Optional.of(cursorInfoWithEmptyField));

    // Call the method under test
    final Map<AirbyteStreamNameNamespacePair, CursorBasedStatus> result =
        PostgresQueryUtils.getCursorBasedSyncStatusForStreams(
            mockDatabase,
            List.of(stream),
            mockStateManager,
            QUOTE_STRING);

    // Verify that the stream is in the result map with a valid status
    assertEquals(1, result.size());

    final AirbyteStreamNameNamespacePair streamPair =
        new AirbyteStreamNameNamespacePair("test_stream", "test_schema");
    final CursorBasedStatus status = result.get(streamPair);

    assertNotNull(status, "Status should not be null for stream with empty cursor field");
    assertEquals("test_stream", status.getStreamName());
    assertEquals("test_schema", status.getStreamNamespace());
    assertEquals(StateType.CURSOR_BASED, status.getStateType());
    assertTrue(status.getCursorField().isEmpty(), "Cursor field should be empty list");
  }

}

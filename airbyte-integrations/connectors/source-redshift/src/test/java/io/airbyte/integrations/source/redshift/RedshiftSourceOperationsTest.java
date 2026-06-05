/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.redshift;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.Calendar;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class RedshiftSourceOperationsTest {

  private RedshiftSourceOperations ops;
  private ResultSet resultSet;
  private ResultSetMetaData metadata;

  @BeforeEach
  void setUp() throws SQLException {
    ops = new RedshiftSourceOperations();
    resultSet = mock(ResultSet.class);
    metadata = mock(ResultSetMetaData.class);
    when(resultSet.getMetaData()).thenReturn(metadata);
  }

  @Test
  void testPutTimestampWithTimezoneDoesNotCallGetString() throws SQLException {
    // Reproduces the StackOverflowError scenario: the Redshift JDBC driver's
    // PGTimestamp.toString() triggers infinite recursion when getString() is
    // called on a timestamptz column. This test verifies that the fixed
    // implementation never calls getString().
    final Instant expected = Instant.parse("2026-06-04T05:50:52.815018Z");
    when(resultSet.getTimestamp(eq(1), any(Calendar.class)))
        .thenReturn(Timestamp.from(expected));

    final ObjectNode node = (ObjectNode) Jsons.emptyObject();
    ops.putTimestampWithTimezone(node, "created_at", resultSet, 1);

    verify(resultSet, never()).getString(anyInt());
    verify(resultSet, never()).getString(any(String.class));

    // Verify the value was written correctly.
    assertFalse(node.isEmpty());
    assertEquals("2026-06-04T05:50:52.815018Z", node.get("created_at").asText());
  }

  @Test
  void testPutTimestampWithTimezoneHandlesNull() throws SQLException {
    when(resultSet.getTimestamp(eq(1), any(Calendar.class))).thenReturn(null);

    final ObjectNode node = (ObjectNode) Jsons.emptyObject();
    ops.putTimestampWithTimezone(node, "created_at", resultSet, 1);

    verify(resultSet, never()).getString(anyInt());
    assertFalse(node.has("created_at"));
  }

  @Test
  void testPutTimestampWithTimezonePreservesSubSecondPrecision() throws SQLException {
    // Redshift supports microsecond precision; verify it's preserved.
    final Instant expected = Instant.parse("2023-11-17T17:50:36.746606Z");
    when(resultSet.getTimestamp(eq(1), any(Calendar.class)))
        .thenReturn(Timestamp.from(expected));

    final ObjectNode node = (ObjectNode) Jsons.emptyObject();
    ops.putTimestampWithTimezone(node, "ts", resultSet, 1);

    final String value = node.get("ts").asText();
    // The output should contain the sub-second component.
    assertEquals("2023-11-17T17:50:36.746606Z", value);
  }

  @Test
  void testCopyToJsonFieldRoutesTimestamptzCorrectly() throws SQLException {
    // Verify that copyToJsonField dispatches timestamptz columns through
    // putTimestampWithTimezone (and therefore avoids getString).
    when(metadata.getColumnTypeName(1)).thenReturn("timestamptz");
    when(metadata.getColumnName(1)).thenReturn("updated_at");

    final Instant expected = Instant.parse("2026-01-15T10:30:00Z");
    when(resultSet.getTimestamp(eq(1), any(Calendar.class)))
        .thenReturn(Timestamp.from(expected));

    final ObjectNode node = (ObjectNode) Jsons.emptyObject();
    ops.copyToJsonField(resultSet, 1, node);

    verify(resultSet, never()).getString(anyInt());
    assertEquals("2026-01-15T10:30:00.000000Z", node.get("updated_at").asText());
  }

}
